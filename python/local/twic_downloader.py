import re
import urllib
import urllib.request
import zipfile
import configparser


def read_webpage():

    # read through TWIC page and find the link that stands for the latest issue
    twic_url = "https://theweekinchess.com/twic"
    # str_source = urllib.urlopen(twic_url).read().decode('utf-8')
    str_source = urllib.request.urlopen(twic_url).read().decode("utf-8")
    last_link = (
        re.findall(r"The latest issue.*\n", str_source)[0]
        .split("=")[1]
        .split(" ")[0]
        .strip('"')
    )
    return last_link


def download_games():

    # define zip filename
    input_zip_filename = "last_twic.zip"

    # download latest TWIC
    last_twic_zip_url = read_webpage().replace(".html", "g.zip").replace("html", "zips")
    urllib.request.urlretrieve(last_twic_zip_url, input_zip_filename)

    # handle zip file
    with zipfile.ZipFile(input_zip_filename, "r") as zip_ref:
        zip_ref.extractall()
        input_pgn_filename = zip_ref.namelist()[0]

    return input_pgn_filename


# print("file as dic: ", read_config("config.cfg"))


def is_rating_relevant(pgn_game):

    cfg = open("python/local/rating.cfg", "r")
    rating = cfg.read()
    cfg.close()
    rating_threshold = int(rating)
    # define rating relevance threshold
    # rating_threshold = 2300
    # rating_threshold = cfg.get("A", "rating")
    # rating = int(input("Qual Rating mínimo ? Ex.: 2300 : "))
    # rating_threshold = rating
    # rating_threshold = int(input("Qual Rating mínimo ? Ex.: 2300 : "))

    # find both ratings in the game
    test = re.findall(r"\n\[.*Elo.*", pgn_game)

    # at least one player was unrated: ratings are not relevant
    if test is None or len(test) != 2:
        return False

    # find numeric values for each rating
    white_elo = int(test[0][12:16])
    black_elo = int(test[1][12:16])

    # both ratings are above threshold: ratings are relevant
    if white_elo > rating_threshold and black_elo > rating_threshold:
        return True

    # otherwise: ratings are irrelevant
    return False


def is_eco_relevant(pgn_game):

    cfg = open("python/local/eco.cfg", "r")
    lista = cfg.read()
    cfg.close()
    eco = lista.split()
    my_repertoire_list = eco

    # define list of interesting ECO codes
    # my_repertoire_list = ["C26", "C28", "C29"]
    # eco = input(
    #    "Digite o código ECO das aberturas separados por espaço. Ex.: C99 B30 A01 C29: "
    # )
    # ecolist = eco.split()
    # my_repertoire_list = ecolist

    # join them into a regular expression
    my_repertoire_re = re.compile("|".join(my_repertoire_list))

    # game used one of those ECO codes: ECO is relevant
    if my_repertoire_re.search(pgn_game):
        return True

    # otherwise: ECO is irrelevant
    return False


def is_game_relevant(pgn_game):

    # rating and ECO conditions are satisfied: game is relevant
    return is_rating_relevant(pgn_game) and is_eco_relevant(pgn_game)


def main():
    # define names of input and output files
    output_pgn_filename = "relevant.pgn"

    input_pgn_filename = download_games()
    all_games = open(input_pgn_filename, "r").read()

    # read input PGN file
    # all_games = open(input_pgn_filename, 'r').read()

    # separate games
    games = re.split(r"\n(?=\[Event  *)", all_games)

    # filter relevant games
    relevant_games = list(filter(is_game_relevant, games))

    # write output PGN file
    output_pgn_file = open(output_pgn_filename, "w")
    for game in relevant_games:
        output_pgn_file.write(game + "\n")
    # create the final zip file
    # with zipfile.ZipFile('teste.zip', 'a') as twiczip:
    #    twiczip.write(output_pgn_filename)
    #    twiczip.write(input_pgn_filename)


main()
