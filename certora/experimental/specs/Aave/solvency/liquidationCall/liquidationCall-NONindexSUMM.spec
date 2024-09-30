
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
import "../common/validation_functions.spec";


/*================================================================================================
  See the README.txt file in the solvency/ directory
  ================================================================================================*/

methods {
  //  function LiquidationLogic._calculateDebt(
  //  DataTypes.ReserveCache memory debtReserveCache,
  //  DataTypes.ExecuteLiquidationCallParams memory params,
  // uint256 healthFactor
  //) internal returns (uint256, uint256) => NONDET;

  function IsolationModeLogic.updateIsolatedDebtIfIsolated(
    mapping(address => DataTypes.ReserveData) storage reservesData,
    mapping(uint256 => address) storage reservesList,
    DataTypes.UserConfigurationMap storage userConfig,
    DataTypes.ReserveCache memory reserveCache,
    uint256 repayAmount
  ) internal => updateIsolatedDebtIfIsolatedCVL();

  function LiquidationLogic._calculateAvailableCollateralToLiquidate(
      DataTypes.ReserveData storage,
      DataTypes.ReserveCache memory,
      address,
      address,
      uint256,
      uint256,
      uint256,
      address // IPriceOracleGetter
  ) internal returns (uint256,uint256,uint256) =>
    _calculateAvailableCollateralToLiquidateCVL();// expects (uint256,uint256,uint256);
    /* difficulty 90 */
}

function _calculateAvailableCollateralToLiquidateCVL() returns (uint256,uint256,uint256) {
  uint256 a;
  uint256 b;
  uint256 c;

  require c==0;
  return (a,b,c);
}


// The function updateIsolatedDebtIfIsolated(...) only writes to the field isolationModeTotalDebt.
function updateIsolatedDebtIfIsolatedCVL() {
  havoc currentContract._reserves[ASSET].isolationModeTotalDebt;
}

/*=====================================================================================
  Rule: same_indexes__liquidationCall
  =====================================================================================*/
rule same_indexes__liquidationCall(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  uint256 __dbtInd_before = getReserveNormalizedVariableDebt(e, _asset);
  uint128 __liqInd_beforeS = reserve.liquidityIndex;
  uint128 __dbtInd_beforeS = reserve.variableBorrowIndex;
  require RAY()<=__liqInd_before && RAY()<=__dbtInd_before;
  require assert_uint128(RAY()) <= __liqInd_beforeS && assert_uint128(RAY()) <= __dbtInd_beforeS;
  

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  bool exists_debt = scaledTotalSupplyCVL(_debt)!=0;
  require exists_debt;

  // THE FUNCTION CALL
  address receiverAddress; uint256 _amount; bytes params; uint16 referralCode; 
  address collateralAsset; address user; uint256 debtToCover; bool receiveAToken;
  liquidationCall(e, collateralAsset, _asset, user, debtToCover, receiveAToken);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  uint128 __liqInd_afterS = reserve2.liquidityIndex;
  uint128 __dbtInd_afterS = reserve2.variableBorrowIndex;
  uint256 __liqInd_after = getNormalizedIncome(e, _asset);
  uint256 __dbtInd_after = getNormalizedDebt(e, _asset);

  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);

  assert __liqInd_after  == __liqInd_before;
  assert assert_uint256(__liqInd_afterS) == __liqInd_after;

  assert __dbtInd_after  == __dbtInd_before;
  assert assert_uint256(__dbtInd_afterS) == __dbtInd_after;
}






/*=====================================================================================
  Rule: solvency__liquidationCall_totDbt_EQ_0  
  =====================================================================================*/
rule solvency__liquidationCall_totDbt_EQ_0(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  //  address _stb = currentContract._reserves[_asset].stableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;
  //require aTokenToUnderlying[_stb]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  uint256 __dbtInd_before = getReserveNormalizedVariableDebt(e, _asset);
  uint128 __liqInd_beforeS = reserve.liquidityIndex;
  uint128 __dbtInd_beforeS = reserve.variableBorrowIndex;
  require RAY()<=__liqInd_before && RAY()<=__dbtInd_before;
  require assert_uint128(RAY()) <= __liqInd_beforeS && assert_uint128(RAY()) <= __dbtInd_beforeS;
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  // BASIC ASSUMPTION FOR THE RULE
  //require scaledTotalSupplyCVL(_stb)==0;
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  uint256 CONST;
  require to_mathint(__totSUP_aToken) <= __virtual_bal + __totSUP_debt + CONST;

  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                    // I believe it's due inaccure RAY-calculations.

  bool exists_debt = scaledTotalSupplyCVL(_debt)!=0;
  require !exists_debt;

  // THE FUNCTION CALL
  address receiverAddress; uint256 _amount; bytes params; uint16 referralCode; 
  address collateralAsset; address user; uint256 debtToCover; bool receiveAToken;
  require receiveAToken==false;
  liquidationCall(e, collateralAsset, _asset, user, debtToCover, receiveAToken);


  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  assert reserve2.liquidityIndex == assert_uint128(__liqInd_before);
  assert getReserveNormalizedIncome(e, _asset) == __liqInd_before;
  
  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt__;   __totSUP_debt__   = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_asset).virtualUnderlyingBalance;
  
  //THE ASSERTION
  assert to_mathint(__totSUP_aToken__) <= __virtual_bal__ + __totSUP_debt__ + CONST
    + reserve2.variableBorrowIndex / RAY() ;
}


