country_codes = {
                "QAT": "Qatar", "ECU": "Ecuador", "SEN": "Senegal", "HOL": "Netherlands",
                "ENG": "England", "IRA": "Iran", "USA": "USA", "WAL": "Wales", 
                "ARG": "Argentina", "SDA": "Saudi Arabia", "MEX": "Mexico", "POL": "Poland",
                "FRA": "France", "AUS": "Australia", "DAN": "Denmark", "TUN": "Tunis",
                "SPA": "Spain", "CTR": "Costa Rica", "TYS": "Germany", "JAP": "Japan",
                "BEL": "Belgium", "KAN": "Canada", "MAR": "Morocco", "KRO": "Croatia", 
                "BRA": "Brazil", "SER": "Serbia", "SUI": "Switzerland", "KAM": "Cameroon",
                "POR": "Portugal", "GHA": "Ghana", "URU": "Uruguay", "SDK": "South Korea"
                }

country_codes_inv = {v: k for k, v in country_codes.items()}

# groups = {
#     "A": {"QAT": "Qatar", "ECU": "Ecuador", "SEN": "Senegal", "HOL": "Netherlands"},
#     "B": {"ENG": "England", "IRA": "Iran", "USA": "USA", "WAL": "Wales"},
#     "C": {"ARG": "Argentina", "SDA": "Saudi Arabia", "MEX": "Mexico", "POL": "Poland"},
#     "D": {"FRA": "France", "AUS": "Australia", "DAN": "Denmark", "TUN": "Tunis"},
#     "E": {"SPA": "Spain", "CTR": "Costa Rica", "TYS": "Germany", "JAP": "Japan"},
#     "F": {"BEL": "Belgium", "KAN": "Canada", "MAR": "Morocco", "KRO": "Croatia"},
#     "G": {"BRA": "Brazil", "SER": "Serbia", "SUI": "Switzerland", "KAM": "Cameroon"},
#     "H": {"POR": "Portugal", "GHA": "Ghana", "URU": "Uruguay", "SDK": "South Korea"}
#     }

grupper = {
        "A": {"QAT": "Qatar", "ECU":"Ecuador", "SEN": "Senegal", "HOL":"Nederländerna"},
        "B": {"ENG": "England", "IRA": "Iran", "USA": "USA", "WAL": "Wales"},
        "C": {"ARG": "Argentina", "SDA": "Saudiarabien", "MEX": "Mexiko", "POL": "Polen"},
        "D": {"FRA": "Frankrike", "AUS": "Australien", "DAN": "Danmark", "TUN": "Tunisien"},
        "E": {"SPA": "Spanien", "CTR": "Costa Rica", "TYS": "Tyskland", "JAP": "Japan"},
        "F": {"BEL": "Belgien", "KAN": "Kanada", "MAR": "Marocko", "KRO": "Kroatien"},
        "G": {"BRA": "Brasilien", "SER": "Serbien", "SUI": "Schweiz", "KAM": "Kamerun"},
        "H": {"POR": "Portugal", "GHA": "Ghana", "URU": "Uruguay", "SDK": "Sydkorea"}
    }

landskod_land_dict = {}
land_landskod_dict = {}
landskod_grupp_dict = {}

for grupp_bokstav, lag_dict in grupper.items():
    for landskod, land in lag_dict.items():
        landskod_land_dict[landskod] = land
        land_landskod_dict[land] = landskod
        landskod_grupp_dict[landskod] = grupp_bokstav

if __name__ == "__main__":
    print("LANDSKODER -> LAND")
    print(landskod_land_dict)
    print("LAND -> LANDSKODER")
    print(land_landskod_dict)
    print("LANDSKOD -> GRUPP")
    print(landskod_grupp_dict)