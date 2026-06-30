# Shader Utility Index

Lookup index for shader-related utility functions in `framework/opengl/gluShader*` files.

Use this file only after a shader generator calls one of these utility functions. The function name is the lookup key. After locating the entry, read the linked source implementation before making any reconstruction claim.

## Declaration Policy

- The primary navigation target is the implementation line.
- Do not duplicate declaration links for ordinary out-of-line functions; the implementation is enough for source inspection.
- Include a header link only when the header is the implementation location, such as `inline` or template functions, or when no implementation is found in the three indexed file pairs.
- If a future declaration contains default parameters or important comments that are absent from the implementation, add a declaration note for that exact function only.

## Indexed File Pairs

| File pair | Leaf namespace |
|-----------|----------------|
| `gluShaderUtil.hpp` / `gluShaderUtil.cpp` | `glu` |
| `gluShaderProgram.hpp` / `gluShaderProgram.cpp` | `glu` |
| `gluShaderLibrary.hpp` / `gluShaderLibrary.cpp` | `sl` under `glu::sl` |

## Leaf namespace `glu`

### `gluShaderUtil`

| Function name | Implementation |
|---------------|----------------|
| `glu::getGLSLVersionName` | [gluShaderUtil.cpp#L35](../../../../framework/opengl/gluShaderUtil.cpp#L35) |
| `glu::getGLSLVersionDeclaration` | [gluShaderUtil.cpp#L45](../../../../framework/opengl/gluShaderUtil.cpp#L45) |
| `glu::glslVersionUsesInOutQualifiers` | [gluShaderUtil.cpp#L56](../../../../framework/opengl/gluShaderUtil.cpp#L56) |
| `glu::glslVersionIsES` | [gluShaderUtil.cpp#L62](../../../../framework/opengl/gluShaderUtil.cpp#L62) |
| `glu::isGLSLVersionSupported` | [gluShaderUtil.cpp#L86](../../../../framework/opengl/gluShaderUtil.cpp#L86) |
| `glu::getContextTypeGLSLVersion` | [gluShaderUtil.cpp#L91](../../../../framework/opengl/gluShaderUtil.cpp#L91) |
| `glu::getShaderTypeName` | [gluShaderUtil.cpp#L106](../../../../framework/opengl/gluShaderUtil.cpp#L106) |
| `glu::getShaderTypePostfix` | [gluShaderUtil.cpp#L118](../../../../framework/opengl/gluShaderUtil.cpp#L118) |
| `glu::getPrecisionName` | [gluShaderUtil.cpp#L125](../../../../framework/opengl/gluShaderUtil.cpp#L125) |
| `glu::getPrecisionPostfix` | [gluShaderUtil.cpp#L134](../../../../framework/opengl/gluShaderUtil.cpp#L134) |
| `glu::getDataTypeName` | [gluShaderUtil.cpp#L141](../../../../framework/opengl/gluShaderUtil.cpp#L141) |
| `glu::getDataTypeScalarSize` | [gluShaderUtil.cpp#L294](../../../../framework/opengl/gluShaderUtil.cpp#L294) |
| `glu::getDataTypeScalarType` | [gluShaderUtil.cpp#L447](../../../../framework/opengl/gluShaderUtil.cpp#L447) |
| `glu::getDataTypeFloat16Scalars` | [gluShaderUtil.cpp#L600](../../../../framework/opengl/gluShaderUtil.cpp#L600) |
| `glu::getDataTypeFloatScalars` | [gluShaderUtil.cpp#L753](../../../../framework/opengl/gluShaderUtil.cpp#L753) |
| `glu::getDataTypeDoubleScalars` | [gluShaderUtil.cpp#L906](../../../../framework/opengl/gluShaderUtil.cpp#L906) |
| `glu::getDataTypeVector` | [gluShaderUtil.cpp#L1059](../../../../framework/opengl/gluShaderUtil.cpp#L1059) |
| `glu::getDataTypeFloatVec` | [gluShaderUtil.cpp#L1082](../../../../framework/opengl/gluShaderUtil.cpp#L1082) |
| `glu::getDataTypeIntVec` | [gluShaderUtil.cpp#L1087](../../../../framework/opengl/gluShaderUtil.cpp#L1087) |
| `glu::getDataTypeUintVec` | [gluShaderUtil.cpp#L1092](../../../../framework/opengl/gluShaderUtil.cpp#L1092) |
| `glu::getDataTypeBoolVec` | [gluShaderUtil.cpp#L1097](../../../../framework/opengl/gluShaderUtil.cpp#L1097) |
| `glu::getDataTypeMatrix` | [gluShaderUtil.cpp#L1102](../../../../framework/opengl/gluShaderUtil.cpp#L1102) |
| `glu::getDataTypeMatrixNumRows` | [gluShaderUtil.cpp#L1108](../../../../framework/opengl/gluShaderUtil.cpp#L1108) |
| `glu::getDataTypeMatrixNumColumns` | [gluShaderUtil.cpp#L1172](../../../../framework/opengl/gluShaderUtil.cpp#L1172) |
| `glu::getDataTypeMatrixColumnType` | [gluShaderUtil.cpp#L1236](../../../../framework/opengl/gluShaderUtil.cpp#L1236) |
| `glu::getDataTypeNumLocations` | [gluShaderUtil.cpp#L1300](../../../../framework/opengl/gluShaderUtil.cpp#L1300) |
| `glu::getDataTypeNumComponents` | [gluShaderUtil.cpp#L1311](../../../../framework/opengl/gluShaderUtil.cpp#L1311) |
| `glu::getDataTypeFromGLType` | [gluShaderUtil.cpp#L1322](../../../../framework/opengl/gluShaderUtil.cpp#L1322) |
| `glu::saveShader` | [gluShaderUtil.cpp#L1533](../../../../framework/opengl/gluShaderUtil.cpp#L1533) |
| `glu::isDataTypeFloat16OrVec` | [gluShaderUtil.hpp#L299](../../../../framework/opengl/gluShaderUtil.hpp#L299) |
| `glu::isDataTypeFloatOrVec` | [gluShaderUtil.hpp#L303](../../../../framework/opengl/gluShaderUtil.hpp#L303) |
| `glu::isDataTypeFloatType` | [gluShaderUtil.hpp#L307](../../../../framework/opengl/gluShaderUtil.hpp#L307) |
| `glu::isDataTypeDoubleType` | [gluShaderUtil.hpp#L311](../../../../framework/opengl/gluShaderUtil.hpp#L311) |
| `glu::isDataTypeDoubleOrDVec` | [gluShaderUtil.hpp#L315](../../../../framework/opengl/gluShaderUtil.hpp#L315) |
| `glu::isDataTypeMatrix` | [gluShaderUtil.hpp#L319](../../../../framework/opengl/gluShaderUtil.hpp#L319) |
| `glu::isDataTypeIntOrIVec` | [gluShaderUtil.hpp#L325](../../../../framework/opengl/gluShaderUtil.hpp#L325) |
| `glu::isDataTypeUintOrUVec` | [gluShaderUtil.hpp#L329](../../../../framework/opengl/gluShaderUtil.hpp#L329) |
| `glu::isDataTypeIntOrIVec8Bit` | [gluShaderUtil.hpp#L333](../../../../framework/opengl/gluShaderUtil.hpp#L333) |
| `glu::isDataTypeUintOrUVec8Bit` | [gluShaderUtil.hpp#L337](../../../../framework/opengl/gluShaderUtil.hpp#L337) |
| `glu::isDataTypeIntOrIVec16Bit` | [gluShaderUtil.hpp#L341](../../../../framework/opengl/gluShaderUtil.hpp#L341) |
| `glu::isDataTypeUintOrUVec16Bit` | [gluShaderUtil.hpp#L345](../../../../framework/opengl/gluShaderUtil.hpp#L345) |
| `glu::isDataTypeBoolOrBVec` | [gluShaderUtil.hpp#L349](../../../../framework/opengl/gluShaderUtil.hpp#L349) |
| `glu::isDataTypeScalar` | [gluShaderUtil.hpp#L353](../../../../framework/opengl/gluShaderUtil.hpp#L353) |
| `glu::isDataTypeVector` | [gluShaderUtil.hpp#L360](../../../../framework/opengl/gluShaderUtil.hpp#L360) |
| `glu::isDataTypeScalarOrVector` | [gluShaderUtil.hpp#L375](../../../../framework/opengl/gluShaderUtil.hpp#L375) |
| `glu::isDataTypeSampler` | [gluShaderUtil.hpp#L384](../../../../framework/opengl/gluShaderUtil.hpp#L384) |
| `glu::isDataTypeImage` | [gluShaderUtil.hpp#L388](../../../../framework/opengl/gluShaderUtil.hpp#L388) |
| `glu::isDataTypeSamplerMultisample` | [gluShaderUtil.hpp#L392](../../../../framework/opengl/gluShaderUtil.hpp#L392) |
| `glu::isDataTypeAtomicCounter` | [gluShaderUtil.hpp#L396](../../../../framework/opengl/gluShaderUtil.hpp#L396) |
| `glu::isDataTypeSamplerBuffer` | [gluShaderUtil.hpp#L400](../../../../framework/opengl/gluShaderUtil.hpp#L400) |
| `glu::isDataTypeSamplerMSArray` | [gluShaderUtil.hpp#L404](../../../../framework/opengl/gluShaderUtil.hpp#L404) |
| `glu::isDataTypeImageBuffer` | [gluShaderUtil.hpp#L408](../../../../framework/opengl/gluShaderUtil.hpp#L408) |
| `glu::isDataTypeExplicitPrecision` | [gluShaderUtil.hpp#L412](../../../../framework/opengl/gluShaderUtil.hpp#L412) |
| `glu::dataTypeSupportsPrecisionModifier` | [gluShaderUtil.hpp#L420](../../../../framework/opengl/gluShaderUtil.hpp#L420) |
| `glu::dataTypeOf` | [gluShaderUtil.hpp#L715](../../../../framework/opengl/gluShaderUtil.hpp#L715) |

### `gluShaderProgram`

| Function name | Implementation |
|---------------|----------------|
| `glu::Shader::setSources` | [gluShaderProgram.cpp#L61](../../../../framework/opengl/gluShaderProgram.cpp#L61) |
| `glu::Shader::compile` | [gluShaderProgram.cpp#L74](../../../../framework/opengl/gluShaderProgram.cpp#L74) |
| `glu::Shader::specialize` | [gluShaderProgram.cpp#L131](../../../../framework/opengl/gluShaderProgram.cpp#L131) |
| `glu::Program::attachShader` | [gluShaderProgram.cpp#L253](../../../../framework/opengl/gluShaderProgram.cpp#L253) |
| `glu::Program::detachShader` | [gluShaderProgram.cpp#L259](../../../../framework/opengl/gluShaderProgram.cpp#L259) |
| `glu::Program::bindAttribLocation` | [gluShaderProgram.cpp#L265](../../../../framework/opengl/gluShaderProgram.cpp#L265) |
| `glu::Program::transformFeedbackVaryings` | [gluShaderProgram.cpp#L271](../../../../framework/opengl/gluShaderProgram.cpp#L271) |
| `glu::Program::link` | [gluShaderProgram.cpp#L277](../../../../framework/opengl/gluShaderProgram.cpp#L277) |
| `glu::Program::isSeparable` | [gluShaderProgram.cpp#L294](../../../../framework/opengl/gluShaderProgram.cpp#L294) |
| `glu::Program::setSeparable` | [gluShaderProgram.cpp#L304](../../../../framework/opengl/gluShaderProgram.cpp#L304) |
| `glu::Program::getUniformLocation` | [gluShaderProgram.hpp#L180](../../../../framework/opengl/gluShaderProgram.hpp#L180) — declaration only in indexed file pairs |
| `glu::ProgramPipeline::useProgramStages` | [gluShaderProgram.cpp#L329](../../../../framework/opengl/gluShaderProgram.cpp#L329) |
| `glu::ProgramPipeline::activeShaderProgram` | [gluShaderProgram.cpp#L335](../../../../framework/opengl/gluShaderProgram.cpp#L335) |
| `glu::ProgramPipeline::isValid` | [gluShaderProgram.cpp#L341](../../../../framework/opengl/gluShaderProgram.cpp#L341) |
| `glu::ShaderProgram::init` | [gluShaderProgram.cpp#L376](../../../../framework/opengl/gluShaderProgram.cpp#L376), [gluShaderProgram.cpp#L435](../../../../framework/opengl/gluShaderProgram.cpp#L435) |
| `glu::ShaderProgram::setBinary` | [gluShaderProgram.cpp#L495](../../../../framework/opengl/gluShaderProgram.cpp#L495) |
| `glu::getGLShaderType` | [gluShaderProgram.cpp#L524](../../../../framework/opengl/gluShaderProgram.cpp#L524) |
| `glu::getGLShaderTypeBit` | [gluShaderProgram.cpp#L547](../../../../framework/opengl/gluShaderProgram.cpp#L547) |
| `glu::getLogShaderType` | [gluShaderProgram.cpp#L570](../../../../framework/opengl/gluShaderProgram.cpp#L570) |
| `glu::makeVtxFragSources` | [gluShaderProgram.hpp#L633](../../../../framework/opengl/gluShaderProgram.hpp#L633) |

## Leaf namespace `sl`

### `gluShaderLibrary`

| Function name | Implementation |
|---------------|----------------|
| `glu::sl::isValid` | [gluShaderLibrary.cpp#L56](../../../../framework/opengl/gluShaderLibrary.cpp#L56), [gluShaderLibrary.cpp#L85](../../../../framework/opengl/gluShaderLibrary.cpp#L85) |
| `glu::sl::isCapabilityRequired` | [gluShaderLibrary.cpp#L230](../../../../framework/opengl/gluShaderLibrary.cpp#L230) |
| `glu::sl::parseFile` | [gluShaderLibrary.cpp#L1756](../../../../framework/opengl/gluShaderLibrary.cpp#L1756) |
| `glu::sl::dumpValues` | [gluShaderLibrary.cpp#L1833](../../../../framework/opengl/gluShaderLibrary.cpp#L1833) |
| `glu::sl::injectExtensionRequirements` | [gluShaderLibrary.cpp#L1853](../../../../framework/opengl/gluShaderLibrary.cpp#L1853) |
| `glu::sl::genCompareFunctions` | [gluShaderLibrary.cpp#L1888](../../../../framework/opengl/gluShaderLibrary.cpp#L1888) |
