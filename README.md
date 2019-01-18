# Azure CLI Disk Copy Extension

This extension enables you to quickly copy disks across resource groups and regions within Azure

[![Build Status](https://dev.azure.com/noelbundick/noelbundick/_apis/build/status/azure-cli-disk-copy-extension?branchName=master)](https://dev.azure.com/noelbundick/noelbundick/_build/latest?definitionId=26?branchName=master)

## How to Use

Use `az extension add` with the [latest release](https://github.com/noelbundick/azure-cli-disk-copy-extension/releases)

## Features

* Works with both managed and unmanaged disks (vhd Page Blobs)
* Copies within the same region or across regions
* Data is copied in the cloud by the Azure Storage service and is not pulled down through your local box
* Uses snapshots to enable copy of currently attached/in-use disks

> Note: You are responsible for copying any additional data written to the disk after the snapshot checkpoint. This may not be needed for a backup/disaster recovery scenario, but would be desired for an app migration

### Commands

* `az disk copy-to-vhd`
* `az disk copy-to-disk`
* `az storage blob copy-to-vhd`
* `az storage blob copy-to-disk`

> Full command details can be accessed via help. Ex: `az storage blob copy-to-vhd --help`

## Development

```bash
export AZURE_EXTENSION_DIR=~/.azure/devcliextensions

pip install --upgrade --target ~/.azure/devcliextensions/disk-copy-extension .
```