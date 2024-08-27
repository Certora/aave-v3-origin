import "erc20.spec";

using StataTokenV2Harness as _StaticATokenLM;
using SymbolicLendingPool as _SymbolicLendingPool;
using RewardsControllerHarness as _RewardsController;
using TransferStrategyHarness as _TransferStrategy;
using DummyERC20_aTokenUnderlying as _DummyERC20_aTokenUnderlying;
using ATokenInstance as _AToken;
using DummyERC20_rewardToken as _DummyERC20_rewardToken;
using ERC4626Storage_Harness as _ERC4626_storage;

/////////////////// Methods ////////////////////////

methods {
    // static aToken
	// -------------
        function asset() external returns (address) envfree;
        function totalAssets() external returns (uint256) envfree;
        function maxWithdraw(address owner) external returns (uint256) envfree;
        function maxRedeem(address owner) external returns (uint256) envfree;
        function previewWithdraw(uint256) external returns (uint256) envfree;
        function previewRedeem(uint256) external returns (uint256) envfree;
        function maxDeposit(address) external returns (uint256);
        function previewMint(uint256) external returns (uint256) envfree;
        function maxMint(address) external returns (uint256);
        function rate() external returns (uint256) envfree;
        function getUnclaimedRewards(address, address) external returns (uint256) envfree;
        function rewardTokens() external returns (address[]) envfree;
        function isRegisteredRewardToken(address) external returns (bool) envfree;
        
    // static aToken harness
    // ---------------------
        function getStaticATokenUnderlying() external returns (address) envfree;
        //function getRewardsIndexOnLastInteraction(address, address) external returns (uint128) envfree;
        //function getRewardTokensLength() external returns (uint256) envfree;
        //function getRewardToken(uint256) external returns (address) envfree;

    // erc20
    // -----
        function _.transferFrom(address,address,uint256) external => DISPATCHER(true);

    // pool
    // ----
        function _SymbolicLendingPool.getReserveNormalizedIncome(address) external returns (uint256) envfree;
        function _SymbolicLendingPool.getReserveData(address) external returns (DataTypes.ReserveData) => CONSTANT;
	
    // rewards controller
	// ------------------
        // In RewardsDistributor.sol called by RewardsController.sol
        function _.getAssetIndex(address, address) external=> DISPATCHER(true);
        // In ScaledBalanceTokenBase.sol called by getAssetIndex
        function _.scaledTotalSupply() external  => DISPATCHER(true);
        // Called by RewardsController._transferRewards()
        // Defined in TransferStrategyHarness as simple transfer() 
        function _.performTransfer(address,address,uint256) external  =>  DISPATCHER(true);

        // harness methods of the rewards controller
        function _RewardsController.getRewardsIndex(address,address) external returns (uint256) envfree;
        function _RewardsController.getAvailableRewardsCount(address) external returns (uint128) envfree;
        function _RewardsController.getRewardsByAsset(address, uint128) external returns (address) envfree;
        function _RewardsController.getAssetListLength() external returns (uint256) envfree;
        function _RewardsController.getAssetByIndex(uint256) external returns (address) envfree;
        function _RewardsController.getDistributionEnd(address, address)  external returns (uint256) envfree;
        function _RewardsController.getUserAccruedRewards(address, address) external returns (uint256) envfree;
        function _RewardsController.getUserAccruedReward(address, address, address) external returns (uint256) envfree;
        function _RewardsController.getAssetDecimals(address) external returns (uint8) envfree;
        function _RewardsController.getRewardsData(address,address) external returns (uint256,uint256,uint256,uint256) envfree;
        function _RewardsController.getUserAssetIndex(address,address, address) external returns (uint256) envfree;

    // underlying token
    // ----------------
        function _DummyERC20_aTokenUnderlying.balanceOf(address) external returns(uint256) envfree;

    // aToken
	// ------
        function _AToken.balanceOf(address) external returns (uint256) envfree;
        function _AToken.totalSupply() external returns (uint256) envfree;
        function _AToken.allowance(address, address) external returns (uint256) envfree;
        function _AToken.UNDERLYING_ASSET_ADDRESS() external returns (address) envfree;
        function _AToken.scaledBalanceOf(address) external returns (uint256) envfree;
        function _AToken.scaledTotalSupply() external returns (uint256) envfree;
        
        // called in aToken
        function _.finalizeTransfer(address, address, address, uint256, uint256, uint256) external => NONDET;
        // Called by rewardscontroller.sol
        // Defined in scaledbalancetokenbase.sol
        function _.getScaledUserBalanceAndSupply(address) external => DISPATCHER(true);

    // reward token
    // ------------
        function _DummyERC20_rewardToken.balanceOf(address) external returns (uint256) envfree;
        function _DummyERC20_rewardToken.totalSupply() external returns (uint256) envfree;

        function _.UNDERLYING_ASSET_ADDRESS() external => CONSTANT UNRESOLVED;

        function RAY() external returns (uint256) envfree;
        //        function get_the_storage() external returns (ERC4626Upgradeable.ERC4626Storage storage) envfree;
        //function ERC4626Upgradeable._getERC4626Storage() internal returns (ERC4626Upgradeable.ERC4626Storage storage) =>
        //  get_the_storage();
}

//function _getERC4626StorageCVL() returns ERC4626Upgradeable.ERC4626Storage {
//  return get_the_storage();
//}


//function getStaticATokenUnderlying() returns address {
//  return _ERC4626_storage._asset; 
//}


///////////////// DEFINITIONS //////////////////////

//    definition RAY() returns uint256 = 10^27;

    /// @notice Claim rewards methods
    definition claimFunctions(method f) returns bool = 
        (f.selector == sig:claimRewardsToSelf(address[]).selector ||
        f.selector == sig:claimRewards(address, address[]).selector ||
        f.selector == sig:claimRewardsOnBehalf(address, address,address[]).selector);
                
    definition collectAndUpdateFunction(method f) returns bool =
        f.selector == sig:collectAndUpdateRewards(address).selector;

/*    definition harnessOnlyMethods(method f) returns bool =
        (harnessMethodsMinusHarnessClaimMethods(f) ||
        f.selector == sig:claimSingleRewardOnBehalf(address, address, address).selector ||
        f.selector == sig:claimDoubleRewardOnBehalfSame(address, address, address).selector);*/
        
/*    definition harnessMethodsMinusHarnessClaimMethods(method f) returns bool =
        (f.selector == sig:getStaticATokenUnderlying().selector ||
        f.selector == sig:getRewardTokensLength().selector ||
        f.selector == sig:getRewardToken(uint256).selector ||
        f.selector == sig:getRewardsIndexOnLastInteraction(address, address).selector ||
        f.selector == sig:getUserRewardsData(address, address).selector ||
        f.selector == sig:_mintWrapper(address, uint256).selector);*/

////////////////// FUNCTIONS //////////////////////

    /**
    * @title Single reward setup
    * Setup the `StaticATokenLM`'s rewards so they contain a single reward token
    * which is` _DummyERC20_rewardToken`.
    */
/*    function single_RewardToken_setup() {
        require getRewardTokensLength() == 1;
        require getRewardToken(0) == _DummyERC20_rewardToken;
        }*/

    /**
    * @title Single reward setup in RewardsController
    * Sets (in `_RewardsController`) the first reward for `_AToken` as
    * `_DummyERC20_rewardToken`.
    */
    function rewardsController_reward_setup() {
        require _RewardsController.getAvailableRewardsCount(_AToken) > 0;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;
    }

    /// @title Assumptions that should hold in any run
    /// @dev Assume that RewardsController.configureAssets(RewardsDataTypes.RewardsConfigInput[] memory rewardsInput) was called
    function setup(env e, address user) {
      /*        require getRewardTokensLength() > 0;*/
        require _RewardsController.getAvailableRewardsCount(_AToken)  > 0;
        require _RewardsController.getRewardsByAsset(_AToken, 0) == _DummyERC20_rewardToken;
        require currentContract != e.msg.sender;
        require currentContract != user;

        require _AToken != user;
        require _RewardsController !=  user;
        require _DummyERC20_aTokenUnderlying  != user;
        require _DummyERC20_rewardToken != user;
        require _SymbolicLendingPool != user;
        require _TransferStrategy != user;
        require _TransferStrategy != user;
    }
