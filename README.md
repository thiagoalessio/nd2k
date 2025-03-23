# nd2k

Converts NovaDAX CSVs reports to formats accepted by Koinly.

[![CI][ci_badge]][ci_project_url]
[![Codacy Badge][codacy_badge]][codacy_project_url]
[![Codacy Coverage Badge][codacy_coverage_badge]][codacy_project_url]

## Requirements

* Python 3.10 or later

## Installation and Usage

	pip3 install https://github.com/thiagoalessio/nd2k/releases/download/v0.1/nd2k-0.1.tar.gz
	nd2k novadax-file.csv

## Key concepts

### Operations and Transactions

* Each line in the NovaDAX CSV is an **Operation**.
* Each line in the Koinly CSV is a **Transaction**.

Transactions can consist of one or more operations:
* A "simple" transaction, such as deposits and withdraws have only one operation.
* A "trade" transaction has three operations (base asset, quote asset, and trading fee).

This script organizes NovaDAX CSV operations into transactions, and outputs
two Koinly CSVs (one for trades and another for all non-trades).

### Base and Quote assets

In a trading pair like BTC/EUR:
* **Base asset (BTC):** The asset being bought or sold.
* **Quote asset (EUR):** The asset used to price the base asset.

## Implementation details

The NovaDAX CSV file must be parsed in reverse order (from the last line to the first)
to correctly match trades with their corresponding fees.

Trading fee lines do not specify which trade they belong to, so we infer the relationship
based on the fee's currency and the trade type (purchase or sale).

* For purchases, the fee is charged in the base asset currency.
* For sales, the fee is charged in the quote asset currency.


---
[ci_badge]: https://github.com/thiagoalessio/nd2k/actions/workflows/ci.yml/badge.svg?event=push&branch=main
[ci_project_url]: https://github.com/thiagoalessio/nd2k/actions/workflows/ci.yml
[codacy_badge]: https://app.codacy.com/project/badge/Grade/e26d4581b014425fba78028573b15f98
[codacy_coverage_badge]: https://app.codacy.com/project/badge/Coverage/e26d4581b014425fba78028573b15f98
[codacy_project_url]: https://app.codacy.com/gh/thiagoalessio/nd2k/dashboard
