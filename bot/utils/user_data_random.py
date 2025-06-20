import string
import random

def get_random_data():
    FIRST_NAMES = [
        "Adam", "Carlos", "Miguel", "Juan", "Luis", "Antonio", "James", "Robert", "John",
        "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles", "Christopher",
        "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
        "Kenneth", "Kevin", "Brian", "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey",
        "Ryan", "Jacob", "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin",
        "Scott", "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander", "Frank", "Patrick",
        "Raymond", "Jack", "Dennis", "Tyler", "Aaron", "Jose", "Henry", "Douglas",
        "Peter", "Walter", "Christian", "Elijah", "Nathan", "Caleb", "Logan", "Mason", "Lucas",
        "Gabriel", "Oscar", "Victor", "Ivan", "Dmitry", "Sergey", "Andrei", "Pavel", "Nikolai",
        "Ricardo", "Fernando", "Alejandro", "Rafael", "Javier", "Diego", "Manuel", "Santiago",
        "Matias", "Sebastian", "Lorenzo", "Marco", "Giovanni", "Vincenzo", "Francesco", "Leonardo",
        "Enzo", "Matteo", "Angelo", "Marcus", "Julius", "Claudio", "Dominic", "Vincent", "Arthur",
        "Louis", "Theodore", "Felix", "Hugo", "Marcel", "Andre", "Kai", "Lukas", "Jonas", "Tobias",
        "Emil", "Kristian", "Magnus", "Leif", "Bjorn", "Erik", "Lars", "Sven", "Ingmar", "Thor"
    ]

    LAST_NAMES = [
        "Perez", "Garcia", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson",
        "Anderson", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Thompson", "White", "Harris",
        "Clark", "Lewis", "Robinson", "Walker", "Young", "Allen", "King", "Wright", "Scott", "Torres",
        "Nguyen", "Hill", "Flores", "Green", "Adams", "Jerry", "Nelson", "Baker", "Hall", "Rivera", "Mitchell",
        "Campbell", "Carter", "Roberts", "Petrov", "Ivanov", "Smirnov", "Volkov", "Kuznetsov", "Popov",
        "Sokolov", "Lebedev", "Kozlov", "Novikov", "Morozov", "Pavlov", "Belyaev", "Vinogradov", "Frolov",
        "Makarenko", "Kravchenko", "Bondarenko", "Tkachenko", "Kovalchuk", "Romanenko", "Savchenko", "Kostenko",
        "Moreno", "Ramirez", "Vargas", "Castillo", "Reyes", "Alvarez", "Mendoza", "Guerrero", "Contreras",
        "Santos", "Costa", "Silva", "Oliveira", "Pereira", "Rodrigues", "Fernandes", "Martins", "Gomes",
        "Ribeiro", "Carvalho", "Cardoso", "Mendes", "Ferreira", "Schmidt", "Weber", "Meyer", "Wagner",
        "Becker", "Schulz", "Hoffmann", "Schneider", "Fischer", "Bauer", "Koch", "Richter", "Klein", "Wolf",
        "Schroder", "Neumann", "Schwarz", "Zimmermann", "Braun", "Hofmann", "Lange", "Schmitt", "Werner",
        "Krause", "Meier", "Lehmann", "Huber", "Kaiser", "Fuchs", "Jensen", "Nielsen", "Hansen", "Pedersen",
        "Andersen", "Christensen", "Larsen", "Sorensen", "Rasmussen", "Olsen", "Johansen", "Mikkelsen", "Eriksen"
    ]

    username = f"{random.choice(FIRST_NAMES)}_{random.choice(LAST_NAMES)}"
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
    server = random.randint(1, 89)
    return username, password, server