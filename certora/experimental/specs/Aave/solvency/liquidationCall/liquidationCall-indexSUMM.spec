
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
  function getReserveDataExtended(address) external returns (DataTypes.ReserveData memory) envfree;

  function ReserveLogic.getNormalizedIncome(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => LIQUIDITY_INDEX;

  function ReserveLogic.getNormalizedDebt(DataTypes.ReserveData storage reserve)
    internal returns (uint256) => DEBT_INDEX;

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
    _calculateAvailableCollateralToLiquidateCVL();
    /* difficulty 90 */
}

function _calculateAvailableCollateralToLiquidateCVL() returns (uint256,uint256,uint256) {
  uint256 a; uint256 b; uint256 c;
  require c==0;

  return (a,b,c);
}


// The function updateIsolatedDebtIfIsolated(...) only writes to the field isolationModeTotalDebt.
function updateIsolatedDebtIfIsolatedCVL() {
  havoc currentContract._reserves[ASSET].isolationModeTotalDebt;
}


ghost uint256 LIQUIDITY_INDEX {axiom LIQUIDITY_INDEX >= 10^27;}
ghost uint256 DEBT_INDEX {axiom DEBT_INDEX >= 10^27;}


/*=====================================================================================
  Rule: solvency__repay
  =====================================================================================*/
rule solvency__liquidationCall(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  tokens_addresses_limitations(_atoken,_debt,_asset);

  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset;

  DataTypes.ReserveData reserve = getReserveDataExtended(_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);
  
  mathint __totSUP_aToken; __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt;  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  // BASIC ASSUMPTION FOR THE RULE
  require isVirtualAccActive(reserve.configuration.data);

  // THE MAIN REQUIREMENT
  uint256 CONST;
  require to_mathint(__totSUP_aToken) <= __virtual_bal + __totSUP_debt + CONST;

  require __totSUP_aToken <= 10^27; // Without this requirement we get a timeout
                                    // I believe it's due inaccure RAY-calculations.
  //require LIQUIDITY_INDEX==10^27;
  //require DEBT_INDEX==2*10^27;

  bool exists_debt = scaledTotalSupplyCVL(_debt)!=0;
  require exists_debt;

  // THE FUNCTION CALL
  address collateralAsset; address user; uint256 debtToCover; bool receiveAToken;
  require receiveAToken==false;
  require collateralAsset != _asset;
  liquidationCall(e, collateralAsset, _asset, user, debtToCover, receiveAToken);
  
  DataTypes.ReserveData reserve2 = getReserveDataExtended(_asset);
  assert reserve2.lastUpdateTimestamp == assert_uint40(e.block.timestamp);
  require assert_uint256(reserve2.liquidityIndex) == LIQUIDITY_INDEX;
  require assert_uint256(reserve2.variableBorrowIndex) == DEBT_INDEX;
  
  mathint __totSUP_aToken__; __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  mathint __totSUP_debt__;   __totSUP_debt__   = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(_asset).virtualUnderlyingBalance;

  assert __totSUP_aToken__ == __totSUP_aToken;
  
  //THE ASSERTION
  assert to_mathint(__totSUP_aToken__) <= __virtual_bal__ + __totSUP_debt__ + CONST
    //+ reserve2.variableBorrowIndex / RAY()
    ;
}

