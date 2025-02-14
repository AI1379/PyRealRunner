# PyRealRunner

**WARNING: the project is still in development and not be able to use.**

A fake runner implemented by python for iOS.

This project is inspired by [iOSRealRun-cli-17](https://github.com/iOSRealRun/iOSRealRun-cli-17), which is not be in development currently. A substantial portion of this project's codebase has been adapted from the referenced repository with necessary modifications.

## Dependencies

We use `poetry` to build the project. Thus, `poetry` is required.

You can use `poetry install` to create a isolated virtual environment as well as installing all dependencies.

## Features

- [ ] Basic runner.
- [ ] Select devices.
- [ ] GUI mode.
- [ ] Support Raspberry Pi.

## Usage

### GUI Mode

<!--TODO-->

### No GUI Mode

<!--TODO-->

## Additional dependencies for Raspberry Pi

To run `kivy` on Raspberry Pi OS, these packages are required by official document of `kivy`:

```bash
apt-get install libgl1-mesa-glx libgles2-mesa libegl1-mesa libmtdev1
```

However it is not quite sure that if `pymobiledevice` is compatible for iOS 17+ on Raspberry Pi. So the support for Raspberry Pi may be delayed.
