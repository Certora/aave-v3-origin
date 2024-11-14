import "./AaveMath.spec";

rule rayMulCVLCorrectness(uint x, uint y) {
    /* simluate rayMul */
    uint solRes = rayMulCVLPrecise(x, y);
    uint cvlRes = rayMulCVL(x, y);
    assert solRes == cvlRes;
}

rule rayDivCVLCorrectness(uint x, uint y) {
    /* simluate rayDiv */
    uint solRes = rayDivCVLPrecise(x, y);
    uint cvlRes = rayDivCVL(x, y);
    assert solRes == cvlRes;
}