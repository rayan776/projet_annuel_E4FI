class Review:

    idReview = None
    idUser = None
    score = None
    content = ""
    dateReview = None
    idAnnounce = None
    username = ""
    firstname = ""
    lastname = ""
    scorePlus = 0
    scoreMinus = 0

    def __init__(self, tupleReview, score_plus, score_minus):
        self.idReview = tupleReview[0]
        self.idUser = tupleReview[1]
        self.score = tupleReview[2]
        self.content = tupleReview[3]
        self.dateReview = tupleReview[4]
        self.idAnnounce = tupleReview[5]
        self.username = tupleReview[6]
        self.firstname = tupleReview[7]
        self.lastname = tupleReview[8]
        self.scorePlus = score_plus
        self.scoreMinus = score_minus