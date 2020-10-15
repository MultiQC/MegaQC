# Changelog

## 0.3.0

### Breaking Changes

- [[#138]](https://github.com/ewels/MegaQC/issues/138) Added `USER_REGISTRATION_APPROVAL` as a config variable, which defaults to true. This means that the admin must explicitly activate new users in the user management page (`/users/admin/users`) before they can login. To disable this feature, you need to create a config file (for example `megaqc.conf.yaml`) with the contents:
  ```yaml
  STRICT_REGISTRATION: false
  ```
  Then, whenever you run MegaQC, you need to `export MEGAQC_CONFIG /path/to/megaqc.conf.yaml
- Much stricter REST API permissions. You now need an API token for almost all requests. One exception is creating a new account, which you can do without a token, but it will be deactivated by default, unless it is the first account created

### New Features

- [[#140]](https://github.com/ewels/MegaQC/issues/140) Added a changelog. It's here! You're reading it!

### Bug Fixes

- [[#139]](https://github.com/ewels/MegaQC/issues/139) Fixed the user management page (`/users/admin/users`), which lost its JavaScript

### Internal Changes

- Tests for the REST API permissions
- Enforce inactive users (by default) in the model layer
