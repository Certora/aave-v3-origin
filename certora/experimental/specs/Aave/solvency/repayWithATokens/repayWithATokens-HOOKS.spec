import "../../../ERC20/WETHcvl.spec";
import "../../../ERC721/erc721.spec";
import "../../../ERC1967/erc1967.spec";
import "../../../PriceAggregators/chainlink.spec";
import "../../../PriceAggregators/tellor.spec";

// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";
import "../../PriceOracleSentinel.spec";
import "../../PriceOracle.spec";
import "../../ACLManager.spec";
import "../../FlashLoanReceiver.spec";

import "../../../problems.spec";
import "../../../unresolved.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";

import "../../../generic.spec"; // pick additional rules from here


/*================================================================================================
  See the README.txt file in the solvency/ directory

  In order to deal with time-outs, we helped the prover by adding several "hooks" inside the function
  executeRepay. In these hooks (see their summarizations below) we added several asserts, hence 
  the prover proves them, and later uses them as requirement for later asserts.
  We run with --multi_asset_check.
  ================================================================================================*/



methods {
  function _.rayMul(uint256 a, uint256 b) internal => rayMulCVLPrecise(a, b) expect uint256; // not optimized well by Prover
  function _.rayDiv(uint256 a, uint256 b) internal => rayDivCVLPrecise(a, b) expect uint256; // seems to be optimized well by Prover
  
  function ValidationLogic.validateRepay(
                                         DataTypes.ReserveCache memory reserveCache,
                                         uint256 amountSent,
                                         DataTypes.InterestRateMode interestRateMode,
                                         address onBehalfOf,
                                         uint256 debt
  ) internal => NONDET;

  function BorrowLogic.repay_hook_1(DataTypes.ReserveCache memory reserveCache)
    internal => repay_hook_1_CVL(reserveCache);
  
  function BorrowLogic.repay_hook_2(DataTypes.ReserveCache memory reserveCache)
    internal with (env e) => repay_hook_2_CVL(e, reserveCache);
  
  function BorrowLogic.repay_hook_3(DataTypes.ReserveCache memory reserveCache, uint256 paybackAmount)
    internal with (env e) => repay_hook_3_CVL(e, reserveCache, paybackAmount);

  function BorrowLogic.repay_hook_4(DataTypes.ReserveCache memory reserveCache)
    internal with (env e) => repay_hook_4_CVL(e, reserveCache);

  //function BorrowLogic.dummy_get_amount() internal returns(uint256) => NONDET;

  function _.havoc_all_dummy() external => HAVOC_ALL;
}

function repay_hook_1_CVL(DataTypes.ReserveCache res) {
  assert currentContract._reserves[ASSET].liquidityIndex == require_uint128(LIQUIDITY_INDEX);
  assert res.nextLiquidityIndex == LIQUIDITY_INDEX;

  assert currentContract._reserves[ASSET].variableBorrowIndex == require_uint128(DEBT_INDEX);
  assert res.nextVariableBorrowIndex == DEBT_INDEX;
}

function repay_hook_2_CVL(env e, DataTypes.ReserveCache res) {
  assert res.nextLiquidityIndex==LIQUIDITY_INDEX;
  assert res.nextVariableBorrowIndex == DEBT_INDEX;
  assert getReserveNormalizedIncome(e, ASSET) == LIQUIDITY_INDEX;
  assert getReserveNormalizedVariableDebt(e, ASSET) == DEBT_INDEX;

  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(DEBT, e));

  // THE MAIN ASSERTION
  assert to_mathint(__totSUP_aToken) <= __totSUP_debt + DELTA;
}

function repay_hook_3_CVL(env e, DataTypes.ReserveCache res, uint256 paybackAmount) {
  assert res.nextLiquidityIndex==LIQUIDITY_INDEX;
  assert res.nextVariableBorrowIndex == DEBT_INDEX;
  assert getReserveNormalizedIncome(e, ASSET) == LIQUIDITY_INDEX;
  assert getReserveNormalizedVariableDebt(e, ASSET) == DEBT_INDEX;
  assert currentContract._reserves[ASSET].lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  assert assert_uint256(currentContract._reserves[ASSET].liquidityIndex) == LIQUIDITY_INDEX;
  assert assert_uint256(currentContract._reserves[ASSET].variableBorrowIndex) == DEBT_INDEX;
  assert VB == currentContract._reserves[ASSET].virtualUnderlyingBalance;
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(DEBT, e));

  // THE MAIN ASSERTION
  assert  to_mathint(__totSUP_aToken) - paybackAmount <= __totSUP_debt + DEBT_INDEX/RAY() + DELTA;
  havoc_all(e);

  // The following requirements are all safe because we've just proved them before the havoc_all.
  mathint __totSUP_aToken2; __totSUP_aToken2 = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  mathint __totSUP_debt2;  __totSUP_debt2 = to_mathint(aTokenTotalSupplyCVL(DEBT, e));
  require res.nextLiquidityIndex==LIQUIDITY_INDEX;
  require res.nextVariableBorrowIndex == DEBT_INDEX;
  require getReserveNormalizedIncome(e, ASSET) == LIQUIDITY_INDEX;
  require getReserveNormalizedVariableDebt(e, ASSET) == DEBT_INDEX;
  require currentContract._reserves[ASSET].lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  require assert_uint256(currentContract._reserves[ASSET].liquidityIndex) == LIQUIDITY_INDEX;
  require assert_uint256(currentContract._reserves[ASSET].variableBorrowIndex) == DEBT_INDEX;
  require VB == currentContract._reserves[ASSET].virtualUnderlyingBalance;

  
  uint256 scaled = totalSupplyByToken[ATOKEN]; uint256 IND = LIQUIDITY_INDEX;
  assert
    to_mathint(rayMulCVLPrecise( require_uint256(scaled - rayDivCVLPrecise(paybackAmount,IND)), IND) )
    <=
    rayMulCVLPrecise(scaled,IND) - paybackAmount + IND/RAY();
}

function repay_hook_4_CVL(env e, DataTypes.ReserveCache res) {
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(ATOKEN, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(DEBT, e));

  // THE MAIN ASSERTION
  assert  to_mathint(__totSUP_aToken) <= __totSUP_debt + DEBT_INDEX/RAY() +
    LIQUIDITY_INDEX/RAY() + DELTA;
}

persistent ghost address ATOKEN; //The current atoken in use. Should be assigned from within the rule.
persistent ghost address DEBT; //The current debt-token in use. Should be assigned from within the rule.
persistent ghost uint256 DELTA;
persistent ghost uint128 VB; // the virtual balance. should not be changed in repayWithATokens.

function _updateIndexesCVL(DataTypes.ReserveCache res) {
  havoc currentContract._reserves[ASSET].liquidityIndex;// assuming
  require currentContract._reserves[ASSET].liquidityIndex == require_uint128(LIQUIDITY_INDEX);
  havoc currentContract._reserves[ASSET].variableBorrowIndex; // assuming
  require currentContract._reserves[ASSET].variableBorrowIndex == require_uint128(DEBT_INDEX);

  require res.nextLiquidityIndex == LIQUIDITY_INDEX;
  require res.nextVariableBorrowIndex == DEBT_INDEX;
}

  
persistent ghost uint256 LIQUIDITY_INDEX {axiom LIQUIDITY_INDEX >= 10^27;}
persistent ghost uint256 DEBT_INDEX {axiom DEBT_INDEX >= 10^27;}


/*=====================================================================================
  Rule: solvency__repayWithATokens
  Status: PASS
  Link: https://prover.certora.com/output/66114/4f2ccd151350485cbc13ae8b6f090592/?anonymousKey=269ecbf902dcd6fa81c201aeed0c7371a605828f
  =====================================================================================*/
rule solvency__repayWithATokens(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress; ATOKEN = _atoken;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress; DEBT = _debt;
  //address _stb = currentContract._reserves[_asset].stableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;
  //require aTokenToUnderlying[_stb]==_asset;

  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  VB = __virtual_bal;

  // INDEXES
  LIQUIDITY_INDEX = getReserveNormalizedIncome(e, _asset);
  DEBT_INDEX = getReserveNormalizedVariableDebt(e, _asset);
  require RAY()  <= LIQUIDITY_INDEX    && RAY()    <= DEBT_INDEX   ;


  // BASIC ASSUMPTION FOR THE RULE
  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);
  //require scaledTotalSupplyCVL(_stb)==0;
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  // Note:
  //    1. DELTA: the gap which the invariant can be break upto. This is a ghost variable
  //    2. We dropped that virtual-balance from the inequality because we prove it stays
  //       unchanged during the function repayWithATokens(...).
  require to_mathint(__totSUP_aToken) <= __totSUP_debt + DELTA;

  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                    // I believe it's due inaccure RAY-calculations.

  bool exists_debt = scaledTotalSupplyCVL(_debt)!=0;
  require exists_debt;

  // THE FUNCTION CALL
  uint256 _amount; uint256 interestRateMode; address onBehalfOf; uint16 referralCode;
  require interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  repayWithATokens(e, _asset, _amount, interestRateMode);
  
  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt__;   __totSUP_debt__   = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  // The virtual-balance stays unchanged
  assert __virtual_bal__==__virtual_bal;

  // THE MAIN ASSERTION
  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  assert to_mathint(__totSUP_aToken__) <= __totSUP_debt__ + DELTA
    + reserve2.liquidityIndex / RAY() + reserve2.variableBorrowIndex / RAY();
}

