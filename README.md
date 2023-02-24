
Sync Bluetooth for dualboot Linux and Windows
=============================================

User-friendly tool making your bluetooth devices working both in Windows and Linux without re-pairing chore.
  [more about dualboot Bluetooth issue](#dualboot-bluetooth-issue)

### bt-dualboot
  * doesn't require to reboot 3 times
  * ask you as much fewer details as possible
  * ... [see all advantages and alternatives](#advantages-and-alternatives)

[How to install](#prerequisites)

**For developers**: checkout the [Developer insights](README-dev.md) for useful development and testings tips.

### Usage: shortest way

Assuming you have paired devices in Windows already, boot to Linux and paired them too.
Syncing would be simple as following 2 steps:

**1. Mount Windows partition**

Application will probe and use mounted Windows partition automatically. Otherwise use [--win /mnt/win/path/](#--win-mntwinpath).
Partition should be mounted with [write access](#troubleshooting-windows-partition-write-access).

**2. Sync all devices available for sync**

```console
$ sudo bt-dualboot --sync-all

Syncing...
==========
 [C2:9E:1D:E2:3D:A5] Keyboard K380
...done

```

NOTES:
  (i) **sudo** tip: this tool needs read-only access to bluetooth devices configuration files which is inaccessible for regular user.
  (ii) [--backup vs --no-backup](#--backup-vs---no-backup): you will be asked about your Windows Registry backup strategy
  (iii) use `--dry-run` to preview any command effects

### Usage: choose device manually

1. List devices info

```console
$ sudo bt-dualboot -l

Works both in Linux and Windows
===============================
 [A4:BF:C6:D0:E5:FF] WH-1000XM4

Needs sync
==========

Following devices available for sync with `--sync-all` or `--sync MAC` options.

 [C2:9E:1D:E2:3D:A5] Keyboard K380

Have to be paired in Windows
============================

Following devices unavailable for sync unless you boot Windows and pair them

 [E9:1D:FE:2A:C3:C8] JBL GO

```


2. Sync devices using MAC

```console
$ sudo bt-dualboot --sync C2:9E:1D:E2:3D:A5

Syncing...
==========
 [C2:9E:1D:E2:3D:A5] Keyboard K380
...done

```

See [`bt-dualboot -h`](#cli-reference) and chapters below for details.

## Prerequisites 

* Python 3.6+ installed.

* `chntpw` package installed:

```console
Ubuntu $ sudo apt install chntpw
...
```

see https://pogostick.net/~pnh/ntpasswd/


## Install

```console
$ sudo pip install bt-dualboot
```

NOTES: **sudo** - application requires read-only access to bluetooth devices configuration files which is inaccessible for regular user. Native OS packages will be added in next releases.

### Supported OS

Tested with Linux Mint 19.3, 20.3 (Ubutntu 18.04 bionic, 20.04 focal), Windows 10

Supported: 

* Potentially any Linux-based systems keeping bluetooth configuration in similar format as Ubuntu
* Windows 10+

With next releases more OSes will be tested, Mac OS support will be added. If you get success or fail results for any OS not listed as supported, please share your experience at https://github.com/x2es/bt-dualboot/issues/1.


## Advanced usage

### --backup vs --no-backup

Windows Registry update performed in the safe way using `chntpw/reged` without changing Hive-file's size (`reged -N -E`). Nevertheless `chntpw` is non-official tool hence backup is not bad idea. Application would perform it as you prefer.

You have to choose your backup strategy explicitly.

```console
$ sudo bt-dualboot --sync-all 
usage: ....
bt-dualboot: error: Neither backup option given!

    Windows Registry Hive file will be updated!
    chntpw/reged tool is non-official and hackish Hive file editing tool.
    It is recommended to do backup prior writing into Hive file.

    Use:
      -b [path], --backup [path]    [default: /var/backup/bt-dualboot]
      -n, --no-backup               process without backup

    WARNING:
        Windows Registry Hive file may contain sensitive data. You shouldn't keep this file
        on a storage which may be accessed by others. Consider to remove backup files as soon
        as possible after ensure Windows boots and works correctly.
```

### --win /mnt/win/path/

By default application will recognize and use mounted Windows partition. In case when it didn't found or more than single Windows partition exist you have to provide mount point with `--win` paramter.

Use `--list-win-mounts` to list recognized Windows partitions.

```console
$ bt-dualboot --list-win-mounts

Windows locations:
==================
 /media/user/win_foo
 /media/user/win_bar
 
$ sudo bt-dualboot --win /media/user/win_foo -l
```

#### Troubleshooting: Windows partition write access

In case when Windows partition mounted in read-only mode, you have to remount it for read-write:

```console
$ sudo mount -o remount,rw /mnt/win/path
```

### Machine processing

`--bot` flag enables better parsable output for usage in scripts.


## Dualboot Bluetooth issue

Every time when a Bluetooth device paired in one dualboot OS it stop working in another one. It happens because both OS uses the same Bluetooth adapter with the same MAC. Each pairing process generates new pairing keys for adapter's MAC. This way previous pairing key which saved in another OS becomes obsolete.

The solution is to sync saved pairing keys for both OS. This answer describes ways to handle this manually: https://unix.stackexchange.com/a/255510/411221

This application implements the way suggested by the [comment](https://unix.stackexchange.com/questions/255509/bluetooth-pairing-on-dual-boot-of-windows-linux-mint-ubuntu-stop-having-to-p#comment545967_255510) which copies pairng keys directly from Linux to Windows avoiding multiple reboots.


## Advantages and alternatives

**bt-dualboot**:

* doesn't require to reboot multiple times
* [simple install](#prerequisites)
* provides single [simple cli](#cli-reference), doesn't require invoke additional scripts
* discower mounted Windows partition automatically
* safe update of Windows Registry without changing file size (rewrite only)
* [backup Windows Registry](#--backup-vs---no-backup) prior update
* doesn't require import/export files, handle encoding issues
* allows `--dry-run` prior actual changes

### alternatives

checkout ["bluetooth dualboot" on github](https://github.com/search?q=bluetooth+dualboot&type=repositories)

**solved by invoke single tool under Linux: sync keys from Linux into Windows registry**: 

(similar approach to bt-dualboot)

* (anounced) https://github.com/nbrideau/bluetooth-key-sync

**solved by invoke multiple tools under Windows and Linux: sync keys from Windows registry into Linux configs**:

(requires more steps and reboots, involves using windows tools, manage import/export files)

Most soulutions is kind of import tool of Windows `*.reg` file into Linux bluetooth configuration.

* [UI] https://github.com/nagi1999a/BluetoothDualBootHelper
* [simple cli] https://github.com/ademlabs/synckeys
* https://github.com/Krakenus/bluetooth-dualboot-fixer
* https://github.com/LondonAppDev/dual-boot-bluetooth-pair
* https://github.com/heyzec/dual-boot-mouse
* https://github.com/arunpandian7/DuoPair-Bluetooth
* https://github.com/luismaf/bluetooth-dual-boot
* [repeative arguments] https://github.com/aryklein/dualBootMouse


**Mac OS**:

* https://github.com/HenrySeed/macosDualBootingBluetoothKeys
* https://github.com/sarneeh/mac-win-dualboot-bt


## Cli reference

```console
$ bt-dualboot -h
usage: bt-dualboot [-h] [-l] [--list-win-mounts] [--bot] [--dry-run] [--win MOUNT] [--sync MAC [MAC ...]] [--sync-all] [-n] [-b [path]]

Sync bluetooth keys from Linux to Windows.

optional arguments:
  -h, --help            show this help message and exit

List resources:
  -l, --list            [root required] list bluetooth devices
  --list-win-mounts     list mounted Windows locations
  --bot                 parsable output for robots (supported: -l)

Sync keys:
  --dry-run             print actions to do without invocation
  --win MOUNT           Windows mount point (advanced usage)
  --sync MAC [MAC ...]  [root required] sync specified device
  --sync-all            [root required] sync all paired devices

Backup Windows Registry:
  -n, --no-backup       process without backup
  -b [path], --backup [path]
                        path to backup directory, default: /var/backup/bt-dualboot
```

## Next releases

First priority is to extend list of tested and supported OS.

General roadmap assumes creating GUI and background service versions, adding sync Linux to Linux ability. It will be implemented on demand - give a voice at https://github.com/x2es/bt-dualboot/issues/2

