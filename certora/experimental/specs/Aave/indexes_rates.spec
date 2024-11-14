import "../ERC20/WETHcvl.spec";
import "../ERC721/erc721.spec";
import "../ERC1967/erc1967.spec";
import "../PriceAggregators/chainlink.spec";
import "../PriceAggregators/tellor.spec";

// aave imports
import "./aToken.spec";
import "./AddressProvider.spec";
import "./PriceOracleSentinel.spec";
import "./PriceOracle.spec";
import "./ACLManager.spec";
//import "./ReserveInterestRateStrategy.spec";
//import "./FlashLoanReceiver.spec";

// standard
import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";



//using DummyWeth as weth;

methods {
  function _.calculateInterestRates(DataTypes.CalculateInterestRatesParams params) external
    => calculateInterestRatesCVL(/*calledContract,*/ params) expect (uint256, uint256, uint256);
}


function calculateInterestRatesCVL(
                                   //    address interestRateStrategy, // redundancy
                                   DataTypes.CalculateInterestRatesParams params
) returns (uint256, uint256, uint256) {
  uint256 liquidityRate; // = liquidityRateModel[params.liquidityAdded - params.liquidityTaken];
  uint256 stableBorrowRate = 0;
  uint256 variableBorrowRate;
  
  require (params.usingVirtualBalance && params.totalStableDebt + params.totalVariableDebt != 0) 
    => params.liquidityTaken <= require_uint256(params.virtualUnderlyingBalance + params.liquidityAdded);
  
  require liquidityRate <= variableBorrowRate;
  return (liquidityRate, stableBorrowRate, variableBorrowRate);
}



//use builtin rule sanity filtered { f -> f.contract == currentContract }


function isVirtualAccActive(uint256 data) returns bool {
    uint mask = 0xEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
    return (data & ~mask) != 0;
}



function init_state() {
  // based on aTokensAreNotUnderlyings
  require forall address a. 
    a == 0 // nothing-token
    || aTokenToUnderlying[a] == 0 // underlying
    || aTokenToUnderlying[aTokenToUnderlying[a]] == 0 // aTokens map to underlyings which map to 0
    ;
  // aTokens have the AToken sort, VariableDebtTokens have the VariableDebt sort, etc...
  require forall address a. tokenToSort[currentContract._reserves[a].aTokenAddress] == AToken_token();
  require forall address a. tokenToSort[currentContract._reserves[a].variableDebtTokenAddress] == VariableDebtToken_token();
  require forall address a. tokenToSort[currentContract._reserves[a].stableDebtTokenAddress] == StableDebtToken_token();
}






rule borrowIndex_GEQ_liquidityIndex__borrow(env e, address _asset) {
  init_state();

  mathint __totSUP_aToken; mathint __totSUP_debt; mathint __totSUP_stb;

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  address _stb = currentContract._reserves[_asset].stableDebtTokenAddress;


  require forall address a. balanceByToken[_debt][a] <= totalSupplyByToken[_debt];
  require forall address a. balanceByToken[_atoken][a] <= totalSupplyByToken[_atoken];
  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset; //require aTokenToUnderlying[_stb]==_asset;

  require _atoken==10; require _debt==11;  require _asset==100;
  require weth!=10 && weth!=11;


  DataTypes.ReserveData reserve1 = getReserveDataExtended(e, _asset);
  uint256 __liq1 = reserve1.liquidityIndex;  uint256 __debt1 = reserve1.variableBorrowIndex;

  require reserve1.lastUpdateTimestamp <= require_uint40(e.block.timestamp); 
  //THE MAIN REQUIREMENT
  require __liq1 <= __debt1;
  require 10^27 <= __liq1  &&  __liq1 <= 2*10^27;
  require reserve1.currentVariableBorrowRate >= reserve1.currentLiquidityRate;
  
  __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));

  require scaledTotalSupplyCVL(_stb)==0;
  require __totSUP_debt!=0;
  uint128 __virtual_bal = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  
  //  require 40 <= __totSUP_aToken && __totSUP_aToken <= 100;
  uint256 _amount; uint256 _interestRateMode; address onBehalfOf; uint16 referralCode;
  require _interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  require isVirtualAccActive(reserve1.configuration.data)==true;
    
  // FUNCTION CALL
  borrow(e, _asset, _amount, _interestRateMode, referralCode, onBehalfOf);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(e, _asset);
  uint256 __liq2 = reserve2.liquidityIndex;  uint256 __debt2 = reserve2.variableBorrowIndex;
  
  //  require reserve2.liquidityIndex == reserve2.variableBorrowIndex;
  //require 10^27 <= reserve2.liquidityIndex  &&  reserve2.liquidityIndex <= 2*10^27;

  assert reserve1.liquidityIndex <= reserve2.liquidityIndex;
  assert reserve1.variableBorrowIndex <= reserve2.variableBorrowIndex;
  assert reserve2.liquidityIndex <= reserve2.variableBorrowIndex;
}


rule test_rayMulDiv() {
  uint256 a; uint256 b;

  require b==10^27;
  uint256 out = rayDivCVLPrecise(rayMulCVLPrecise(a,b),b);

  assert out==a;
  
  assert (out-a)*b <= 10^27 / 2 + b/2;
  assert out-a <= (10^27 / 2 + b/2)/b;
  assert to_mathint(out) <= a + (5*10^26)/b + 1;
  assert to_mathint(out) <= a + (5*10^26)/b;
}
