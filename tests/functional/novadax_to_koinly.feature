Feature: Convert NovaDAX CSV to Koinly-compatible transactions
	As a crypto trader
	I want to convert my NovaDAX operation history
	So I can import it into Koinly for tax reporting

	Scenario: Convert NovaDAX operations to Koinly transactions
		Given a NovaDAX CSV file has the following operations:
			| date                | summary                       | symbol   | amount                              | status  |
			| 23/09/2024 20:13:47 | Redeemed Bonus                | BRL      | R$ +5,00                            | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL)          | MEMERUNE | +362,77 MEMERUNE(≈R$155.05)         | Sucesso |
			| 28/09/2024 17:19:53 | Venda(MEMERUNE/BRL)           | BRL      | R$ +89,48                           | Sucesso |
			| 27/10/2024 12:29:24 | Depósito de criptomoedas      | PUNKAI   | +1,609,546,768462 PUNKAI(≈R$160.95) | Sucesso |
			| 28/09/2024 17:19:54 | Taxa de transação             | BRL      | R$ -0,39                            | Sucesso |
			| 28/09/2024 17:19:53 | Taxa de transação             | BRL      | R$ -0,39                            | Falha   |
			| 28/09/2024 17:18:43 | Taxa de transação             | MEMERUNE | -1,559911 MEMERUNE(≈R$0.67)         | Sucesso |
			| 28/09/2024 17:19:53 | Venda(MEMERUNE/BRL)           | MEMERUNE | -205,19 MEMERUNE(≈R$87.58)          | Sucesso |
			| 28/09/2024 17:18:43 | Compra(MEMERUNE/BRL)          | BRL      | R$ -155,04                          | Sucesso |
			| 23/09/2024 20:01:41 | Depósito em Reais             | BRL      | R$ +50,000,00                       | Falha   |
			| 23/09/2024 20:01:41 | Depósito em Reais             | BRL      | R$ +40,000,00                       | Sucesso |
			| 28/09/2024 07:08:35 | Taxa de transação             | TIP      | -863,3841 TIP(≈R$0.22)              | Sucesso |
			| 24/10/2024 16:19:22 | Taxa de saque de criptomoedas | DCR      | -0,01 DCR(≈R$0.69)                  | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)               | TIP      | +200,787,00 TIP(≈R$51.02)           | Sucesso |
			| 24/10/2024 16:19:22 | Saque de criptomoedas         | DCR      | -1,54256146 DCR(≈R$106.55)          | Sucesso |
			| 28/09/2024 07:08:35 | Compra(TIP/BRL)               | BRL      | R$ -51,01                           | Sucesso |

		When they are processed

		Then a Koinly trades file should be created with the following transactions:
			| date                | pair         | side |    amount |  total | fee_amount | fee_currency | orderid | tradeid |
			| 2024-09-28 17:18:43 | MEMERUNE/BRL | BUY  |    362.77 | 155.04 |   1.559911 | MEMERUNE     |         |         |
			| 2024-09-28 17:19:53 | MEMERUNE/BRL | SELL |    205.19 |  89.48 |   0.39     | BRL          |         |         |
			| 2024-09-28 07:08:35 | TIP/BRL      | BUY  | 200787.00 |  51.01 | 863.3841   | TIP          |         |         |

		Then a Koinly non_trades file should be created with the following transactions:
			| date                |           amount | symbol   | tag      | txhash |
			| 2024-09-23 20:13:47 |       5.00       | BRL      | reward   |        |
			| 2024-10-27 12:29:24 | 1609546.768462   | PUNKAI   | deposit  |        |
			| 2024-09-23 20:01:41 |   40000.00       | BRL      | deposit  |        |
			| 2024-10-24 16:19:22 |       0.01       | DCR      | fee      |        |
			| 2024-10-24 16:19:22 |       1.54256146 | DCR      | withdraw |        |
