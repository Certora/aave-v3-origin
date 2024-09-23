// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.19;
pragma experimental ABIEncoderV2;

import {EModeConfiguration} from '../munged/contracts/protocol/libraries/configuration/EModeConfiguration.sol';
import {DataTypes} from '../munged/contracts/protocol/libraries/types/DataTypes.sol';

contract EModeConfigurationHarness {
  DataTypes.EModeCategory public eModeCategory;

  function setCollateral(uint256 reserveIndex,bool collateral) public {
    DataTypes.EModeCategory memory emode_new = eModeCategory;
    EModeConfiguration.setCollateral(emode_new, reserveIndex, collateral);
    eModeCategory.isCollateralBitmap = emode_new.isCollateralBitmap;
  }

  function isCollateralAsset(uint256 reserveIndex) public returns (bool) {
    return EModeConfiguration.isCollateralAsset(eModeCategory.isCollateralBitmap, reserveIndex);
  }


  function setBorrowable(uint256 reserveIndex,bool borrowable) public {
    DataTypes.EModeCategory memory emode_new = eModeCategory;
    EModeConfiguration.setBorrowable(emode_new, reserveIndex, borrowable);
    eModeCategory.isBorrowableBitmap = emode_new.isBorrowableBitmap;
  }

  function isBorrowableAsset(uint256 reserveIndex) public returns (bool) {
    return EModeConfiguration.isBorrowableAsset(eModeCategory.isBorrowableBitmap, reserveIndex);
  }


  /*

  // Sets the Loan to Value of the reserve
  function setLtv(uint256 ltv) public {
    DataTypes.ReserveConfigurationMap memory configNew = reservesConfig;
    ReserveConfiguration.setLtv(configNew, ltv);
    reservesConfig.data = configNew.data;
  }

  // Gets the Loan to Value of the reserve
  function getLtv() public view returns (uint256) {
    return ReserveConfiguration.getLtv(reservesConfig);
  }
  */
}
