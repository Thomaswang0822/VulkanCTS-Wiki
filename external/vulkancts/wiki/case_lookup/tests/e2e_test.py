#!/usr/bin/env python3
"""Small browser E2E for the localhost prototype using Chromium CDP."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path

import websockets

CASES = (
    (
        "dEQP-VK.api.buffer.basic.max_size",
        "api/Buffer",
    ),
    (
        "dEQP-VK.api.copy_and_blit.copy_commands2.buffer_to_image.1d_images.array_all_remaining_layers",
        "api/CopyBufferToImage",
    ),
    (
        "dEQP-VK.api.copy_and_blit.copy_memory_indirect.use_after_copy.a1r5g5b5_unorm_pack16.general.32x32x1",
        "api/UseAfterCopy",
    ),
    (
        "dEQP-VK.api.copy_and_blit.core.memory_to_image_indirect.2d_images.array",
        "api/CopyMemoryIndirect",
    ),
    (
        "dEQP-VK.rasterization.culling.back_triangle_fan",
        "rasterization/Core",
    ),
    (
        "dEQP-VK.rasterization.fill_rules_multisample_16_bit.basic_quad",
        "rasterization/Core",
    ),
    (
        "dEQP-VK.rasterization.depth_bias_control.d16_unorm.float_exact.constant.constant_depth_0_125.target_bias_0_0625.dynamic_set_2_clamp_to_half",
        "rasterization/DepthBiasControl",
    ),
)


class CDP:
    def __init__(self, websocket):
        self.websocket = websocket
        self.message_id = 0

    async def call(self, method: str, params: dict | None = None) -> dict:
        self.message_id += 1
        message_id = self.message_id
        await self.websocket.send(
            json.dumps({"id": message_id, "method": method, "params": params or {}})
        )
        while True:
            message = json.loads(await self.websocket.recv())
            if message.get("id") == message_id:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message.get("result", {})

    async def evaluate(self, expression: str) -> object:
        result = await self.call(
            "Runtime.evaluate",
            {"expression": expression, "returnByValue": True, "awaitPromise": True},
        )
        return result["result"].get("value")


async def run_e2e(debug_port: int, base_url: str) -> list[dict[str, object]]:
    targets = json.load(urllib.request.urlopen(f"http://127.0.0.1:{debug_port}/json"))
    page = next(target for target in targets if target["type"] == "page")
    results: list[dict[str, object]] = []

    async with websockets.connect(page["webSocketDebuggerUrl"]) as websocket:
        cdp = CDP(websocket)
        await cdp.call("Page.enable")
        await cdp.call("Runtime.enable")
        await cdp.call("Page.navigate", {"url": base_url})
        for _ in range(100):
            if await cdp.evaluate("document.readyState") == "complete":
                break
            await asyncio.sleep(0.05)

        for _ in range(100):
            if await cdp.evaluate("document.querySelector('#path').disabled") is False:
                break
            await asyncio.sleep(0.05)
        else:
            raise RuntimeError("Static lookup mappings did not finish loading")

        for path, expected in CASES:
            await cdp.evaluate(
                "document.querySelector('#path').value = "
                + json.dumps(path)
                + "; document.querySelector('#lookup-form').requestSubmit();"
            )
            text = ""
            for _ in range(100):
                text = str(await cdp.evaluate("document.querySelector('#result').innerText"))
                if "查询中" not in text:
                    break
                await asyncio.sleep(0.05)
            results.append(
                {"path": path, "expected": expected, "actual": text, "pass": expected in text}
            )

        await cdp.evaluate(
            "document.querySelector('#path').value = 'dEQP-VK.api.not_a_real_family.case';"
            "document.querySelector('#lookup-form').requestSubmit();"
        )
        no_match = str(await cdp.evaluate("document.querySelector('#result').innerText"))
        results.append(
            {
                "path": "dEQP-VK.api.not_a_real_family.case",
                "expected": "当前索引中没有对应的 Level-3 页面",
                "actual": no_match,
                "pass": "当前索引中没有对应的 Level-3 页面" in no_match,
            }
        )

        await cdp.evaluate(
            "document.querySelector('#path').value = 'api.buffer.basic.max_size';"
            "document.querySelector('#lookup-form').requestSubmit();"
        )
        invalid = ""
        for _ in range(100):
            invalid = str(await cdp.evaluate("document.querySelector('#result').innerText"))
            if "查询中" not in invalid:
                break
            await asyncio.sleep(0.05)
        results.append(
            {
                "path": "api.buffer.basic.max_size",
                "expected": "请输入以 dEQP-VK. 开头",
                "actual": invalid,
                "pass": "请输入以 dEQP-VK. 开头" in invalid,
            }
        )
        # The suite uses one page only and closes it explicitly before Chromium exits.
        await cdp.call("Page.close")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765/")
    parser.add_argument("--debug-port", type=int, default=9229)
    args = parser.parse_args()

    with tempfile.TemporaryDirectory() as profile:
        chromium = subprocess.Popen(
            [
                "chromium",
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                f"--remote-debugging-port={args.debug_port}",
                f"--user-data-dir={profile}",
                "about:blank",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            for _ in range(100):
                try:
                    urllib.request.urlopen(
                        f"http://127.0.0.1:{args.debug_port}/json/version", timeout=1
                    )
                    break
                except Exception:
                    time.sleep(0.05)
            else:
                raise RuntimeError("Chromium CDP did not become ready")

            results = asyncio.run(run_e2e(args.debug_port, args.url))
        finally:
            chromium.terminate()
            try:
                chromium.wait(timeout=5)
            except subprocess.TimeoutExpired:
                chromium.kill()
                chromium.wait(timeout=5)

    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(result["pass"] for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
