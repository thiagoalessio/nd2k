Feature: Convert NovaDAX CSV to Koinly-compatible transactions
	As a crypto trader
	I want to convert my NovaDAX operation history
	So I can import it into Koinly for tax reporting

	Scenario: Convert NovaDAX operations to Koinly transactions
		Given a NovaDAX CSV file has the following operations:
			| date                | summary                       | symbol   | amount                              | status  |
			| 19/11/2024 12:25:50 | Saque em Reais                | BRL      | R$ -8,900,00                        | Sucesso |
			| 23/09/2024 20:13:47 | Redeemed Bonus                | BRL      | R$ +5,00                            | Sucesso |
			| 23/09/2024 20:13:47 | Redeemed Bonus                | BRL      | R$ +5,00                            | Sucesso |
			| 28/09/2024 17:18:43 | Taxa de transação             | MEMERUNE | -4,00 MEMERUNE(≈R$0.67)             | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL)          | BRL      | R$ -100,00                          | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL)          | MEMERUNE | +400,00 MEMERUNE(≈R$155.05)         | Sucesso |
			| 07/07/2023 06:30:16 | Troca                         | EFGH     | +29,294,567743 VMPXBRC(≈R$29294.57) | Sucesso |
			| 07/07/2023 06:30:16 | Troca                         | ABCD     | -29,294,567743 VMPX(≈R$11274.01)    | Sucesso |
			| 07/07/2023 06:30:16 | Troca                         | VMPXBRC  | +29,294,567743 VMPXBRC(≈R$29294.57) | Sucesso |
			| 07/07/2023 06:30:16 | Troca                         | VMPX     | -29,294,567743 VMPX(≈R$11274.01)    | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL)          | MEMERUNE | +362,77 MEMERUNE(≈R$155.05)         | Sucesso |
			| 28/09/2024 17:19:53 | Venda(MEMERUNE/BRL)           | BRL      | R$ +89,48                           | Sucesso |
			| 30/08/2023 03:47:09 | Taxa de Convert               | BRL      | R$ -0,01                            | Sucesso |
			| 30/08/2023 03:47:09 | Convert                       | BRL      | R$ +0,12                            | Sucesso |
			| 30/08/2023 03:47:09 | Convert                       | MATIC    | -0,04322 MATIC(≈R$0.12)             | Sucesso |
			| 30/08/2023 03:47:09 | Taxa de Convert               | BRL      | R$ -0,01                            | Sucesso |
			| 30/08/2023 03:47:09 | Convert                       | BRL      | R$ +0,22                            | Sucesso |
			| 30/08/2023 03:47:09 | Convert                       | DOGE     | -0,705 DOGE(≈R$0.22)                | Sucesso |
			| 27/10/2024 12:29:24 | Depósito de criptomoedas      | PUNKAI   | +1,609,546,768462 PUNKAI(≈R$160.95) | Sucesso |
			| 28/09/2024 17:19:54 | Taxa de transação             | BRL      | R$ -0,39                            | Sucesso |
			| 28/09/2024 17:19:53 | Taxa de transação             | BRL      | R$ -0,39                            | Falha   |
			| 28/09/2024 17:18:43 | Taxa de transação             | MEMERUNE | -1,559911 MEMERUNE(≈R$0.67)         | Sucesso |
			| 28/09/2024 17:19:53 | Venda(MEMERUNE/BRL)           | MEMERUNE | -205,19 MEMERUNE(≈R$87.58)          | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL)          | BRL      | R$ -155,04                          | Sucesso |
			| 23/09/2024 20:01:41 | Depósito em Reais             | BRL      | R$ +50,000,00                       | Falha   |
			| 23/09/2024 20:01:41 | Depósito em Reais             | BRL      | R$ +40,000,00                       | Sucesso |
			| 28/09/2024 07:08:35 | Taxa de transação             | TIP      | -863,3841 TIP(≈R$0.22)              | Sucesso |
			| 24/10/2024 16:19:23 | Taxa de saque de criptomoedas | DCR      | -0,01 DCR(≈R$0.69)                  | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)               | TIP      | +200,787,00 TIP(≈R$51.02)           | Sucesso |
			| 24/10/2024 16:19:22 | Saque de criptomoedas         | DCR      | -1,54256146 DCR(≈R$106.55)          | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)               | BRL      | R$ -51,01                           | Sucesso |
			| 01/01/1970 00:00:00 | Saque de criptomoedas         | SHIB     | 1000                                | Sucesso |
			| 01/01/1970 00:00:00 | Saque de criptomoedas         | DOGE     |  500                                | Sucesso |

		When the file is processed

		Then a Koinly universal file should be created with the following transactions:
			| date                | sent_amount    | sent_cur | recv_amount    | recv_cur | fee_amount | fee_cur  | nwa | nwc | label    | description                   | txh |
			| 1970-01-01 00:00:00 |   500          | DOGE     |                |          |            |          |     |     | withdraw | Saque de criptomoedas         |     |
			| 1970-01-01 00:00:00 |  1000          | SHIB     |                |          |            |          |     |     | withdraw | Saque de criptomoedas         |     |
			| 2023-07-07 06:30:16 | 29294.567743   | VMPX     |   29294.567743 | VMPXBRC  |            |          |     |     | swap     | Troca                         |     |
			| 2023-07-07 06:30:16 | 29294.567743   | ABCD     |   29294.567743 | EFGH     |            |          |     |     | swap     | Troca                         |     |
			| 2023-08-30 03:47:09 |     0.705      | DOGE     |       0.22     | BRL      | 0.01       | BRL      |     |     | exchange | Convert                       |     |
			| 2023-08-30 03:47:09 |     0.04322    | MATIC    |       0.12     | BRL      | 0.01       | BRL      |     |     | exchange | Convert                       |     |
			| 2024-09-23 20:01:41 |                |          |   40000.00     | BRL      |            |          |     |     | deposit  | Depósito em Reais             |     |
			| 2024-09-23 20:13:47 |                |          |      10.00     | BRL      |            |          |     |     | reward   | Redeemed Bonus                |     |
			| 2024-09-28 07:08:35 |    51.01       | BRL      |  200787.00     | TIP      | 863.3841   | TIP      |     |     | trade    | Compra(TIP/BRL)               |     |
			| 2024-09-28 17:18:43 |   255.04       | BRL      |     762.77     | MEMERUNE |   5.559911 | MEMERUNE |     |     | trade    | Compra(MEMERUNE/BRL)          |     |
			| 2024-09-28 17:19:53 |   205.19       | MEMERUNE |      89.48     | BRL      |   0.39     | BRL      |     |     | trade    | Venda(MEMERUNE/BRL)           |     |
			| 2024-10-24 16:19:22 |     1.54256146 | DCR      |                |          |            |          |     |     | withdraw | Saque de criptomoedas         |     |
			| 2024-10-24 16:19:23 |     0.01       | DCR      |                |          |            |          |     |     | fee      | Taxa de saque de criptomoedas |     |
			| 2024-10-27 12:29:24 |                |          | 1609546.768462 | PUNKAI   |            |          |     |     | deposit  | Depósito de criptomoedas      |     |
			| 2024-11-19 12:25:50 |  8900.00       | BRL      |                |          |            |          |     |     | withdraw | Saque em Reais                |     |


	Scenario: NovaDAX file is incomplete
		Given a NovaDAX CSV file has the following operations:
			| date                | summary              | symbol   | amount                      | status  |
			| 28/09/2024 17:18:43 | Taxa de transação    | MEMERUNE | -4,00 MEMERUNE(≈R$0.67)     | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL) | BRL      | R$ -100,00                  | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL) | MEMERUNE | +362,77 MEMERUNE(≈R$155.05) | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)      | TIP      | +200,787,00 TIP(≈R$51.02)   | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)      | BRL      | R$ -51,01                   | Sucesso |
			| 28/09/2024 17:19:53 | Venda(MEMERUNE/BRL)  | BRL      | R$ +89,48                   | Sucesso |
			| 28/09/2024 17:19:54 | Taxa de transação    | BRL      | R$ -0,39                    | Sucesso |
			| 28/09/2024 17:18:43 | Taxa de transação    | MEMERUNE | -1,559911 MEMERUNE(≈R$0.67) | Sucesso |
			| 28/09/2024 17:19:53 | Venda(MEMERUNE/BRL)  | MEMERUNE | -205,19 MEMERUNE(≈R$87.58)  | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL) | BRL      | R$ -155,04                  | Sucesso |
			| 28/09/2024 07:08:35 | Taxa de transação    | TIP      | -863,3841 TIP(≈R$0.22)      | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)      | TIP      | +200,787,00 TIP(≈R$51.02)   | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)      | BRL      | R$ -51,01                   | Sucesso |

		When I attempt to process the file

		Then the following error should appear:
			"""
			Error! The script went through all rows in the NovaDAX CSV and could not find a match for the following operations:

			( 'Incomplete Trades',
			  [ PartialTrade(summary='Compra(TIP/BRL)',
			                 trading_pair=TradingPair(base='TIP', quote='BRL'),
			                 base_asset=Operation(date=datetime.datetime(2024, 9, 28, 7, 8, 35),
			                                      type=<OperationType.BUY: 'Compra'>,
			                                      summary='Compra(TIP/BRL)',
			                                      symbol='TIP',
			                                      amount=Decimal('200787.00'),
			                                      status='Sucesso'),
			                 quote_asset=Operation(date=datetime.datetime(2024, 9, 28, 7, 8, 35),
			                                       type=<OperationType.BUY: 'Compra'>,
			                                       summary='Compra(TIP/BRL)',
			                                       symbol='BRL',
			                                       amount=Decimal('51.01'),
			                                       status='Sucesso'),
			                 trading_fee=None),
			    PartialTrade(summary='Compra(MEMERUNE/BRL)',
			                 trading_pair=TradingPair(base='MEMERUNE', quote='BRL'),
			                 base_asset=None,
			                 quote_asset=Operation(date=datetime.datetime(2024, 9, 28, 17, 18, 43),
			                                       type=<OperationType.BUY: 'Compra'>,
			                                       summary='Compra(MEMERUNE/BRL)',
			                                       symbol='BRL',
			                                       amount=Decimal('100.00'),
			                                       status='Sucesso'),
			                 trading_fee=Operation(date=datetime.datetime(2024, 9, 28, 17, 18, 43),
			                                       type=<OperationType.TRADING_FEE: 'Taxa de transação'>,
			                                       summary='Taxa de transação',
			                                       symbol='MEMERUNE',
			                                       amount=Decimal('4.00'),
			                                       status='Sucesso'))])

			The input file may be faulty, or the script misinterpreted its contents.
			If you are sure the input file is correct, please open an issue at https://github.com/thiagoalessio/nd2k/issues/new and attach the file that caused this error.
			"""
