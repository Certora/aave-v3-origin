// SPDX-License-Identifier: BUSL-1.1
pragma solidity ^0.8.10;

import {IPool, DataTypes} from '../../../core/contracts/interfaces/IPool.sol';
import {IERC20Metadata} from 'solidity-utils/contracts/oz-common/interfaces/IERC20Metadata.sol';
import {ITransparentProxyFactory} from 'solidity-utils/contracts/transparent-proxy/interfaces/ITransparentProxyFactory.sol';
import {Initializable} from 'solidity-utils/contracts/transparent-proxy/Initializable.sol';
import {StataTokenV2} from './StataTokenV2.sol';
import {IStataTokenFactory} from './interfaces/IStataTokenFactory.sol';

/**
 * @title StataTokenFactory
 * @notice Factory contract that keeps track of all deployed StataTokens for a specified pool.
 * This registry also acts as a factory, allowing to deploy new StataTokens on demand.
 * There can only be one StataToken per underlying on the registry at any time.
 * @author BGD labs
 */
contract StataTokenFactory is Initializable, IStataTokenFactory {
  IPool public immutable POOL;
  address public immutable PROXY_ADMIN;
  ITransparentProxyFactory public immutable TRANSPARENT_PROXY_FACTORY;
  address public immutable STATIC_A_TOKEN_IMPL;

  mapping(address => address) internal _underlyingToStaticAToken;
  address[] internal _staticATokens;

  event StaticTokenCreated(address indexed staticAToken, address indexed underlying);

  constructor(
    IPool pool,
    address proxyAdmin,
    ITransparentProxyFactory transparentProxyFactory,
    address staticATokenImpl
  ) {
    POOL = pool;
    PROXY_ADMIN = proxyAdmin;
    TRANSPARENT_PROXY_FACTORY = transparentProxyFactory;
    STATIC_A_TOKEN_IMPL = staticATokenImpl;
  }

  function initialize() external initializer {}

  ///@inheritdoc IStataTokenFactory
  function createStataTokens(address[] memory underlyings) external returns (address[] memory) {
    address[] memory staticATokens = new address[](underlyings.length);
    for (uint256 i = 0; i < underlyings.length; i++) {
      address cachedStaticAToken = _underlyingToStaticAToken[underlyings[i]];
      if (cachedStaticAToken == address(0)) {
        DataTypes.ReserveDataLegacy memory reserveData = POOL.getReserveData(underlyings[i]);
        if (reserveData.aTokenAddress == address(0))
          revert NotListedUnderlying(reserveData.aTokenAddress);
        bytes memory symbol = abi.encodePacked(
          'stat',
          IERC20Metadata(reserveData.aTokenAddress).symbol(),
          'v2'
        );
        address staticAToken = TRANSPARENT_PROXY_FACTORY.createDeterministic(
          STATIC_A_TOKEN_IMPL,
          PROXY_ADMIN,
          abi.encodeWithSelector(
            StataTokenV2.initialize.selector,
            reserveData.aTokenAddress,
            string(
              abi.encodePacked('Static ', IERC20Metadata(reserveData.aTokenAddress).name(), ' v2')
            ),
            string(symbol)
          ),
          bytes32(uint256(uint160(underlyings[i])))
        );

        _underlyingToStaticAToken[underlyings[i]] = staticAToken;
        staticATokens[i] = staticAToken;
        _staticATokens.push(staticAToken);
        emit StaticTokenCreated(staticAToken, underlyings[i]);
      } else {
        staticATokens[i] = cachedStaticAToken;
      }
    }
    return staticATokens;
  }

  ///@inheritdoc IStataTokenFactory
  function getStataTokens() external view returns (address[] memory) {
    return _staticATokens;
  }

  ///@inheritdoc IStataTokenFactory
  function getStataToken(address underlying) external view returns (address) {
    return _underlyingToStaticAToken[underlying];
  }
}
