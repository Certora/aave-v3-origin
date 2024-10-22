
// aave imports
import "../../aToken.spec";
import "../../AddressProvider.spec";

import "../common/optimizations.spec";
import "../common/functions.spec";
//import "../common/validation_functions.spec";


methods {
  function LiquidationLogic.HOOK_liquidation_after_calculateDebt(uint256 userTotalDebt)
    internal => HOOK_liquidation_after_calculateDebt_CVL(userTotalDebt);

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
  
function HOOK_liquidation_after_calculateDebt_CVL(uint256 userTotalDebt) {
  assert userTotalDebt==0;
}


// The function updateIsolatedDebtIfIsolated(...) only writes to the field isolationModeTotalDebt.
function updateIsolatedDebtIfIsolatedCVL() {
  address asset;
  havoc currentContract._reserves[asset].isolationModeTotalDebt;
}

function _calculateAvailableCollateralToLiquidateCVL() returns (uint256,uint256,uint256) {
  uint256 a; uint256 b; uint256 c;  require c==0;
  return (a,b,c);
}



persistent ghost address _DBT_asset; persistent ghost address _DBT_atoken; persistent ghost address _DBT_debt;
persistent ghost uint256 _DBT_liqIND; persistent ghost uint256 _DBT_dbtIND;

persistent ghost address _COL_asset; persistent ghost address _COL_atoken; persistent ghost address _COL_debt;
persistent ghost uint256 _COL_liqIND; persistent ghost uint256 _COL_dbtIND;



function tokens_addresses_limitations_LQD(address asset, address atoken, address debt,
                                          address asset2, address atoken2, address debt2
                                         ) {
  require asset==100;  require atoken==10;  require debt==11; 
  require asset2==200; require atoken2==20; require debt2==21; 
}


function configuration() {
  init_state();

  _DBT_atoken = currentContract._reserves[_DBT_asset].aTokenAddress;
  _COL_atoken = currentContract._reserves[_COL_asset].aTokenAddress;            
  _DBT_debt = currentContract._reserves[_DBT_asset].variableDebtTokenAddress;
  _COL_debt = currentContract._reserves[_COL_asset].variableDebtTokenAddress;
  tokens_addresses_limitations_LQD(_DBT_asset, _DBT_atoken, _DBT_debt,
                                   _COL_asset, _COL_atoken, _COL_debt);

  require aTokenToUnderlying[_DBT_atoken]==_DBT_asset; require aTokenToUnderlying[_DBT_debt]==_DBT_asset;
  require aTokenToUnderlying[_COL_atoken]==_COL_asset; require aTokenToUnderlying[_COL_debt]==_COL_asset;
}



/*=====================================================================================
  Rule: liquidationCall_must_revert_if_totDebt_of_DBTasset_EQ_0
  =====================================================================================*/
rule liquidationCall_must_revert_if_totDebt_of_DBTasset_EQ_0(env e) {
  init_state();

  configuration();

  DataTypes.ReserveData reserve = getReserveDataExtended(_DBT_asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // BASIC ASSUMPTION FOR THE RULE
  //  require isVirtualAccActive(reserve.configuration.data);

  require scaledTotalSupplyCVL(_DBT_debt)==0;

  // THE FUNCTION CALL
  address user; uint256 debtToCover; bool receiveAToken;
  // TODO: prove the following basic erc20 property
  require aTokenBalanceOfCVL(_DBT_debt,user,e) <= scaledTotalSupplyCVL(_DBT_debt);
  liquidationCall@withrevert(e, _COL_asset, _DBT_asset, user, debtToCover, receiveAToken);

  assert lastReverted;
}



