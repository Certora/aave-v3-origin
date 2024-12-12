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
import "./ReserveInterestRateStrategy.spec";
import "./FlashLoanReceiver.spec";

// standard
import "../problems.spec";
import "../unresolved.spec";
import "../optimizations.spec";

import "../generic.spec"; // pick additional rules from here


//using DummyWeth as weth;

methods {
  function _.ADDRESSES_PROVIDER() external => NONDET; // expect address

  function ReserveLogic.getNormalizedIncome(DataTypes.ReserveData storage reserve) internal returns (uint256);
     
  function _.calculateInterestRates(DataTypes.CalculateInterestRatesParams params) external
    => NONDET;
  
  //    function getIsVirtualAccActive(DataTypes.ReserveConfigurationMap memory self) internal returns (bool) envfree;

    // envfree
    // function getReserveDataExtended(address) external returns (DataTypes.ReserveData memory) envfree; // use direct storage access instead
}

use builtin rule sanity filtered { f -> f.contract == currentContract }

// Simple rule - depends on better summaries for `IReserveInterestRateStrategy` OR linking it (with the risk of longer running time)
// See in https://prover.certora.com/output/60724/b7043622211340e98e602bd4e46c9aff/?anonymousKey=ff16ebf727d2aa6631a187c862a845a624bf64a5
// by filtering for `virtualUnderlyingBalance` accesses in the trace
rule user_withdraw_cannot_surpass_VA() {
  env e;
  uint256 amount;
  address to;
  address asset;
  uint128 virtual_bal_before = currentContract._reserves[asset].virtualUnderlyingBalance;
  withdraw(e,asset, amount, to);
  assert amount <= assert_uint256(virtual_bal_before);
}

function isVirtualAccActive(uint256 data) returns bool {
    uint mask = 0xEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF;
    return (data & ~mask) != 0;
}

// for an asset in the reserves, it's aToken's totalSupply is not bigger than the virtualUnderlyingBalance
invariant virtualUnderlyingBalanceLessThanATokenTotalSupply(env e, address asset)
    to_mathint(currentContract._reserves[asset].virtualUnderlyingBalance) 
        <= to_mathint(aTokenTotalSupplyCVL(currentContract._reserves[asset].aTokenAddress, e))
filtered { f -> f.contract == currentContract }
    {
        preserved with (env eF) {
            init_state();
            require eF.block.timestamp == e.block.timestamp;
            require eF.block.number == e.block.number;
            // here's the weird one - we initialize the currentLiquidityRate to be liquidityRateModel[0],
            // so if the function we call increases liquidity, the currentLiquidityRate will decrease,
            // and if the function we call decreases liquidity, the currentLiquidityRate will increase
            require require_uint256(currentContract._reserves[asset].currentLiquidityRate) == liquidityRateModel[0];
            // let's also require that we use the virtual balance
            require isVirtualAccActive(currentContract._reserves[asset].configuration.data);
            requireInvariant reserveAssetsAreATokenUnderlyingsFORALL();
            require asset != 0; // there's no asset in address 0 (we could also define that the aTokenAddress of 0 is 0 and prove it - it should verify xxx)
        }
    }

/**
    This pair of rules is really the same and should be merged to one definition xxx.
    The idea is to use the forall version in requireInvariant,
    and the non-forall version for easier debugging of the check (it's a stronger version which is 'pointwise', so proving it also proves the forall).
    It currently fails on:
    1. `initReserve` - because initReserve does not check that the provided aToken's underlying is the asset we want. To check if that's an issue or not.
    2. `flashLoan` because I'm not dealing with the havocs it has currently. xxx
 */
invariant reserveAssetsAreATokenUnderlyingsFORALL()
    // if `asset` is initialized as a reserve:
    forall address asset. currentContract._reserves[asset].aTokenAddress != 0 => 
        aTokenToUnderlying[currentContract._reserves[asset].aTokenAddress] == asset
filtered { f -> f.contract == currentContract }

invariant reserveAssetsAreATokenUnderlyings(address asset)
    // if `asset` is initialized as a reserve:
    currentContract._reserves[asset].aTokenAddress != 0 => 
        aTokenToUnderlying[currentContract._reserves[asset].aTokenAddress] == asset
filtered { f -> f.contract == currentContract }
    
// a legitimate hard rule
invariant supply_gte_debt(env e, address asset) 
    to_mathint(aTokenTotalSupplyCVL(currentContract._reserves[asset].aTokenAddress, e))
        >= (
            aTokenTotalSupplyCVL(currentContract._reserves[asset].variableDebtTokenAddress, e) // totalVariable
            + aTokenTotalSupplyCVL(currentContract._reserves[asset].stableDebtTokenAddress, e) // totalStable
        )
filtered { f -> f.contract == currentContract }
{
    preserved {
        init_state();
    }
}

// exploratory rules
rule changes_virtual_underlying_balance(method f)
filtered { f -> f.contract == currentContract }
{
    address asset;
    uint _virtualUnderlyingBalance = currentContract._reserves[asset].virtualUnderlyingBalance;

    env e;
    calldataarg arg;
    f(e, arg);

    uint virtualUnderlyingBalance_ = currentContract._reserves[asset].virtualUnderlyingBalance;

    satisfy _virtualUnderlyingBalance != virtualUnderlyingBalance_, "Does not update virtual underlying balance";
}

rule changes_aToken_supply(method f)
filtered { f -> f.contract == currentContract }
{
    env e;
    address asset;
    address aToken = currentContract._reserves[asset].aTokenAddress;
    uint _aTokenTotalSupply = aTokenTotalSupplyCVL(aToken, e);

    env eF;
    require eF.block.timestamp == e.block.timestamp;
    require eF.block.number == e.block.number;
    calldataarg arg;
    f(e, arg);
    
    uint aTokenTotalSupply_ = aTokenTotalSupplyCVL(aToken, e);

    satisfy _aTokenTotalSupply != aTokenTotalSupply_, "Does not update an aToken's total supply";
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





rule supply_gte_debt__deposit(env e, address asset) {
  init_state();

  mathint total_supply_Atoken;
  mathint total_supply_var;
  mathint total_supply_stb;

  address atoken = currentContract._reserves[asset].aTokenAddress;
  address debt = currentContract._reserves[asset].variableDebtTokenAddress;
  address stb = currentContract._reserves[asset].stableDebtTokenAddress;

  require atoken==10;
  require debt==11;
  require stb==12;

  require asset==100;

  DataTypes.ReserveData reserves = getReserveDataExtended(e, asset);
  //  require reserves.lastUpdateTimestamp == require_uint40(e.block.timestamp);
  
  total_supply_Atoken = to_mathint(aTokenTotalSupplyCVL(atoken, e));
  total_supply_var = to_mathint(aTokenTotalSupplyCVL(debt, e));
  //  total_supply_stb = to_mathint(aTokenTotalSupplyCVL(stb, e));

  require aTokenToUnderlying[atoken]==asset;
  require aTokenToUnderlying[debt]==asset;
  //  require aTokenToUnderlying[stb]==asset;

  require total_supply_Atoken >= total_supply_var //+ total_supply_stb;
    ;
  //  address asset;
  uint256 amount;
  address onBehalfOf;
  uint16 referralCode;
    
  deposit(e, asset, amount, onBehalfOf, referralCode);

  assert  
    //to_mathint(
               aTokenTotalSupplyCVL(currentContract._reserves[asset].aTokenAddress, e)
    //)
    >= (
        aTokenTotalSupplyCVL(currentContract._reserves[asset].variableDebtTokenAddress, e) // totalVariable
        //        + aTokenTotalSupplyCVL(currentContract._reserves[asset].stableDebtTokenAddress, e) // totalStable
    );
    
}



rule supply_gte_debt__borrow(env e, address _asset) {
  init_state();

  mathint _total_supply_Atoken; mathint _total_supply_var;//, _total_supply_stb;

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  address _stb = currentContract._reserves[_asset].stableDebtTokenAddress;

  require _atoken==10; require _debt==11; require _stb==12; require _asset==100;
  require weth!=10 && weth!=11 && weth!=12;
  

  DataTypes.ReserveData reserves = getReserveDataExtended(e, _asset);
    require reserves.lastUpdateTimestamp == require_uint40(e.block.timestamp);
  require reserves.liquidityIndex == reserves.variableBorrowIndex;
    require reserves.liquidityIndex == 10^27;
  
  _total_supply_Atoken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  _total_supply_var = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  //  _total_supply_stb = to_mathint(aTokenTotalSupplyCVL(_stb, e));

  require aTokenToUnderlying[_atoken]==_asset;
  require aTokenToUnderlying[_debt]==_asset;
  //  require aTokenToUnderlying[_stb]==_asset;

  require _total_supply_Atoken >= _total_supply_var; //+ _total_supply_stb;
  require _total_supply_Atoken <= 100;
  uint256 _amount;
  uint256 _interestRateMode;

    require forall address a. balanceByToken[_debt][a] <= totalSupplyByToken[_debt];
  require forall address a. balanceByToken[_atoken][a] <= totalSupplyByToken[_atoken];

  address onBehalfOf;
  uint16 referralCode;
  require _interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  bool _is_VA_active = reserves.configuration.data &~0xEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF != 0;
  require _is_VA_active == true;
  uint128 _virtual_bal_before = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  require to_mathint(_virtual_bal_before) <= _total_supply_Atoken - _total_supply_var;

  borrow(e, _asset, _amount, _interestRateMode, referralCode, onBehalfOf);

  assert  
    //to_mathint(
               aTokenTotalSupplyCVL(currentContract._reserves[_asset].aTokenAddress, e)
    //)
    >= (
        aTokenTotalSupplyCVL(currentContract._reserves[_asset].variableDebtTokenAddress, e) // totalVariable
        //        + aTokenTotalSupplyCVL(currentContract._reserves[_asset].stableDebtTokenAddress, e) // totalStable
    );
}








rule virtual_plus_debt_LEQ_supply__borrow(env e, address _asset) {
  init_state();

  mathint __totSUP_aToken; mathint __totSUP_debt;

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  address _stb = currentContract._reserves[_asset].stableDebtTokenAddress;

  require forall address a. balanceByToken[_debt][a] <= totalSupplyByToken[_debt];
  require forall address a. balanceByToken[_atoken][a] <= totalSupplyByToken[_atoken];
  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset; //require aTokenToUnderlying[_stb]==_asset;

  require _atoken==10; require _debt==11; require _stb==12; require _asset==100;
  require weth!=10 && weth!=11 && weth!=12;


  DataTypes.ReserveData reserve = getReserveDataExtended(e, _asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp); 
  require reserve.liquidityIndex == reserve.variableBorrowIndex;
  require 10^27 <= reserve.liquidityIndex  &&  reserve.liquidityIndex <= 2*10^27;
  //  require reserve.currentVariableBorrowRate==reserve.currentLiquidityRate;
  

  __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  //  __total_supply_stb = to_mathint(aTokenTotalSupplyCVL(_stb, e));
  uint128 __virtual_bal = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  //THE MAIN REQUIREMENT
  require __virtual_bal + __totSUP_debt <= to_mathint(__totSUP_aToken);
  
  require 40 <= __totSUP_aToken && __totSUP_aToken <= 100;
  uint256 _amount; uint256 _interestRateMode; address onBehalfOf; uint16 referralCode;
  require _interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  bool _is_VA_active = reserve.configuration.data &~0xEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF != 0;
  require _is_VA_active == true;

  // FUNCTION CALL
  borrow(e, _asset, _amount, _interestRateMode, referralCode, onBehalfOf);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(e, _asset);
  require reserve2.liquidityIndex == reserve2.variableBorrowIndex;
  require 10^27 <= reserve2.liquidityIndex  &&  reserve2.liquidityIndex <= 2*10^27;


  mathint __totSUP_aToken__; mathint __totSUP_debt__;
  __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt__ = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  
  assert __virtual_bal__ + __totSUP_debt__ <= to_mathint(__totSUP_aToken__)+1;
}




rule borrowIndex_GEQ_liquidityIndex__borrow(env e, address _asset) {
  init_state();

  mathint __totSUP_aToken; mathint __totSUP_debt;

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;


  require forall address a. balanceByToken[_debt][a] <= totalSupplyByToken[_debt];
  require forall address a. balanceByToken[_atoken][a] <= totalSupplyByToken[_atoken];
  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset; //require aTokenToUnderlying[_stb]==_asset;

  require _atoken==10; require _debt==11;  require _asset==100;
  require weth!=10 && weth!=11;


  DataTypes.ReserveData reserve = getReserveDataExtended(e, _asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp); 
  //THE MAIN REQUIREMENT
  require reserve.liquidityIndex <= reserve.variableBorrowIndex;
  require 10^27 <= reserve.liquidityIndex  &&  reserve.variableBorrowIndex <= 2*10^27;
  //  require reserve.currentVariableBorrowRate==reserve.currentLiquidityRate;
  

  __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  //  __total_supply_stb = to_mathint(aTokenTotalSupplyCVL(_stb, e));
  uint128 __virtual_bal = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  //  require __virtual_bal + __totSUP_debt <= to_mathint(__totSUP_aToken);
  
  require 40 <= __totSUP_aToken && __totSUP_aToken <= 100;
  uint256 _amount; uint256 _interestRateMode; address onBehalfOf; uint16 referralCode;
  require _interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  bool _is_VA_active = reserve.configuration.data &~0xEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF != 0;
  require _is_VA_active == true;

  // FUNCTION CALL
  borrow(e, _asset, _amount, _interestRateMode, referralCode, onBehalfOf);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(e, _asset);
  //  require reserve2.liquidityIndex == reserve2.variableBorrowIndex;
  require 10^27 <= reserve2.liquidityIndex  &&  reserve2.liquidityIndex <= 2*10^27;

  /*
  mathint __totSUP_aToken__; mathint __totSUP_debt__;
  __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt__ = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  assert __virtual_bal__ + __totSUP_debt__ <= to_mathint(__totSUP_aToken__)+1;*/

  assert reserve2.liquidityIndex <= reserve2.variableBorrowIndex;
}






rule virtual_plus_debt_EQ_supply_plus_accued__borrow(env e, address _asset) {
  init_state();

  address _atoken = currentContract._reserves[_asset].aTokenAddress;
  address _debt = currentContract._reserves[_asset].variableDebtTokenAddress;
  address _stb = currentContract._reserves[_asset].stableDebtTokenAddress;
  require _atoken==10; require _debt==11; require _stb==12; require _asset==100;
  require weth!=10 && weth!=11 && weth!=12;

  require forall address a. balanceByToken[_debt][a] <= totalSupplyByToken[_debt];
  require forall address a. balanceByToken[_atoken][a] <= totalSupplyByToken[_atoken];
  require aTokenToUnderlying[_atoken]==_asset; require aTokenToUnderlying[_debt]==_asset; require aTokenToUnderlying[_stb]==_asset;


  DataTypes.ReserveData reserve = getReserveDataExtended(e, _asset);
  require reserve.lastUpdateTimestamp <= require_uint40(e.block.timestamp);

  // INDEXES REQUIREMENTS
  uint128 __liqInd_beforeOLD = reserve.liquidityIndex;
  uint128 __dbtInd_beforeOLD = reserve.variableBorrowIndex;
  uint256 __liqInd_before = getReserveNormalizedIncome(e, _asset);
  uint256 __dbtInd_before = getReserveNormalizedVariableDebt(e, _asset);
  
  require                RAY()  <= __liqInd_before    && __liqInd_before    <= __dbtInd_before   ;
  require assert_uint128(RAY()) <= __liqInd_beforeOLD && __liqInd_beforeOLD <= __dbtInd_beforeOLD;
  //require 10^27 <= reserve.liquidityIndex  &&  reserve.liquidityIndex <= 2*10^27;
  //  require __liqInd_beforeOLD ==assert_uint128(RAY()); require __dbtInd_beforeOLD == assert_uint128(RAY() + RAY()/10);
  //require __liqInd_before ==RAY(); require __dbtInd_before == assert_uint256(RAY() + RAY()/10);

  require reserve.currentLiquidityRate <= reserve.currentVariableBorrowRate;
  
  mathint __totSUP_aToken; mathint __totSUP_debt; mathint __totSUP_stb;
  __totSUP_aToken = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  __totSUP_stb = to_mathint(aTokenTotalSupplyCVL(_stb, e));
  require scaledTotalSupplyCVL(_stb)==0;
  uint128 __virtual_bal = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  uint128 __accrued = reserve.accruedToTreasury;
  //THE MAIN REQUIREMENT
  //require __virtual_bal + __totSUP_debt ==
  //  to_mathint(__totSUP_aToken) + rayMulCVLPrecise(__accrued,reserve.liquidityIndex);
  require to_mathint(__totSUP_aToken) <= __virtual_bal + __totSUP_debt;
  
  require 40 <= __totSUP_aToken && __totSUP_aToken <= 100;
  uint256 _amount; uint256 _interestRateMode; address onBehalfOf; uint16 referralCode;
  require _interestRateMode == assert_uint256(DataTypes.InterestRateMode.VARIABLE);
  bool _is_VA_active = reserve.configuration.data &~0xEFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF != 0;
  require _is_VA_active == true;

  // FUNCTION CALL
  borrow(e, _asset, _amount, _interestRateMode, referralCode, onBehalfOf);

  DataTypes.ReserveData reserve2 = getReserveDataExtended(e, _asset);
  //require reserve2.liquidityIndex == reserve2.variableBorrowIndex;
  //  require 10^27 <= reserve2.liquidityIndex  &&  reserve2.liquidityIndex <= 2*10^27;
  uint128 __liqInd_afterOLD = reserve2.liquidityIndex;
  uint128 __dbtInd_afterOLD = reserve2.variableBorrowIndex;
  uint256 __liqInd_after = getReserveNormalizedIncome(e, _asset);
  uint256 __dbtInd_after = getReserveNormalizedVariableDebt(e, _asset);


  mathint __totSUP_aToken__; mathint __totSUP_debt__;
  __totSUP_aToken__ = to_mathint(aTokenTotalSupplyCVL(_atoken, e));
  __totSUP_debt__ = to_mathint(aTokenTotalSupplyCVL(_debt, e));
  uint128 __virtual_bal__ = getReserveDataExtended(e,_asset).virtualUnderlyingBalance;
  
  //assert __virtual_bal__ + __totSUP_debt__ <=
  //to_mathint(__totSUP_aToken__) + rayMulCVLPrecise(__accrued,reserve2.liquidityIndex) + 1;
  //assert to_mathint(__totSUP_aToken__) + rayMulCVLPrecise(__accrued,reserve2.liquidityIndex)
  //  <= __virtual_bal__ + __totSUP_debt__ + 1;

  //PURE SOLVENCY
  assert to_mathint(__totSUP_aToken__) <= __virtual_bal__ + __totSUP_debt__ + rayDivCVLPrecise(__dbtInd_after,RAY()) ;
}
