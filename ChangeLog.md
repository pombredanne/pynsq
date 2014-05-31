# Changelog

## 0.6.2 - 2014-02-21

IMPORTANT: this is a bug-fix release to address an issue where `Reader` would raise
and exception when receiving a heartbeat.

 * #68 - fix heartbeat_interval bug

## 0.6.1 - 2014-02-17

IMPORTANT: this is a bug-fix release to address an issue preventing `Reader` from
consuming messages.

 * #63 - fix connection attributes bug; `heartbeat_interval` as ms
 * #65 - fix invalid arguments during read error
 * #66/#64 - add integration tests; improve testing matrix

## 0.6.0 - 2014-02-13

This release includes an array of new features, refactoring, and bug fixes.

Primarily, support for sampling channels, modifying output buffering, enabling
Snappy compression, and setting user agent metadata.

Finally, there was a large *internal* refactoring in #52 to achieve better separation of
concerns and pep8 compliance in #53.

 * #59 - add `nsq_to_nsq` example app (thanks [@ploxiln](https://github.com/ploxiln))
 * #58 - add user agent `IDENTIFY` metadata
 * #57 - add channel sampling feature negotiation
 * #55 - update `Message` docs (thanks [@dsoprea](https://github.com/dsoprea))
 * #53 - pep8
 * #52 - evented refactoring
 * #49 - add output buffering feature negotiation
 * #50 - add Snappy compression feature negotiation
 * #51 - fix periodic timers when not configuring `nsqlookupd`

## 0.5.1 - 2013-08-19

This is a bug-fix release addressing a few issues in `Writer`.

 * #48 - fix writer encoding issues
 * #47 - fix writer uncaught exception when no connections to publish to
 * #45 - fix writer id property

## 0.5.0 - 2013-07-26

This release drops the concept of "tasks" in `Reader` (in favor of a single message handler). This
greatly simplifies internal RDY state handling and is a cleaner API as we head towards 1.0.

These changes modify the public API and break backwards compatibility. To ease the transition we've
added a `LegacyReader` class that accepts the previous version's arguments and facilitates
instantiating new `Reader` instances for each task with the same automatic channel naming
conventions.

We suggest you begin to migrate towards using the new API directly (`LegacyReader` will not be
in the 1.0 release), but for now the upgrade is as simple as:

    from nsq import LegacyReader as Reader

Finally, TLS support is available via `tls_v1` and `tls_options` params to `Reader` (available in
`nsqd` as of `0.2.22+`).

 * #42 - TLS support
 * #39 - distribute requests to lookupd
 * #38 - fix edge case where conn would never get RDY; RDY fairness when # conns > max_in_flight
 * #36/#37 - refactor internal connection, backoff, and RDY handling
 * #29/#34/#35 - refactor public API (drop "tasks"); improve RDY count handling
 * #28/#31 - improve backoff handling

## 0.4.2 - 2013-05-09

 * #25 - add Writer
 * #24 - add is_starved to Reader

## 0.4.1 - 2013-04-22

 * #23 - fix Message export, cleanup IDENTIFY response logging

## 0.4.0 - 2013-04-19

 * #22 - feature negotiation (supported by nsqd v0.2.20+)
         wait 2x heartbeat interval before closing conns
         more logging improvements
 * #21 - configurable heartbeat interval (supported by nsqd v0.2.19+)
 * #17 - add task to all connection related logging; ensure max_in_flight is never < # tasks
 * #16 - always set initial RDY count to 1
 * #14 - automatically reconnect to nsqd when not using lookupd
 * #12 - cleanup/remove deprecated async=True
 * #9 - redistribute ready state when max_in_flight < num_conns

## 0.3.4 - 2013-02-20
 
 * #10 - fix parameter type for REQ
 * #8 - add tests
 * #6 - fix TOUCH; deprecate `async=True` in favor of always using message instance methods

## 0.3.2 - 2013-01-31

 * #4 - TOUCH support; new message response API (deprecates `finisher`)

## 0.3.1 - 2013-01-07

 * #5 - add/use IDENTIFY
 * #1 - check topic/channel length for validity

## 0.3.0 - 2012-10-31

 * Initial Release
