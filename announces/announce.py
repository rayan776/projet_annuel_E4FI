import ast
from project_1coup2pouce.mysqlConnectionSingleton import MySQLConnectionSingleton
from project_1coup2pouce.users import Users
import project_1coup2pouce.misc as misc
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
from datetime import datetime
from announces.review import Review

class Announce:

    mySqlConnector = None
    COEFF_LONGITUDE = 0.02
    COEFF_LATITUDE = 0.01
    DEFAULT_LATITUDE = 0
    DEFAUT_LONGITUDE = 0
    geolocator = None

    def __init__(self):
        self.mySqlConnector = MySQLConnectionSingleton()
        self.geolocator = Nominatim(user_agent="1coup2pouce")

    def get_categories(self):
        """
            récupère toutes les catégories d'annonce existantes en base de données
        """
        categories = self.mySqlConnector.execute_prepared_query("SELECT * FROM category",tuple(),True)
        categories_dict = [{'idCategory': cat[0], 'categoryName': cat[1]} for cat in categories]
        return categories_dict
    
    def get_announce(self, request, idAnnounce, isAdmin):
        values = []
        values.append(idAnnounce)
        sql_query = f"SELECT idAnnounce, typeAnnounce, dateAnnounce, intitule, description, latitude, longitude, localisation, valid, idCat, idUser, catName, username, firstname, lastname FROM announce INNER JOIN users USING (idUser) INNER JOIN category using (idCat) WHERE idAnnounce = %s "
        if not isAdmin:
            sql_query = sql_query + " AND (valid = 1"
            if request.session.get("logged_user", False):
                sql_query = sql_query + f" OR valid = 0 AND idUser = %s) "
                values.append(request.session["idUser"])
            else:
                sql_query = sql_query + ") "
                

        results = self.mySqlConnector.execute_prepared_query(sql_query, tuple(values), True)
        if len(results) == 0:
            results = None
        else:
            results = results[0]
        
        return results
    
    def get_announces(self, request, default=True):
        """
            retourne une liste d'annonces conformément aux critères de recherche

            default (booléen) : si on veut faire une recherche par défaut (toutes les annonces)
            ou si on veut chercher selon des critères spécifiques
        """
        users = Users()
        search_params = dict()
        values = []
        first_where = True
        select_unapproved_announces = request.session.get("logged_user", False) and users.getLevel(request, request.session["login"]) == "admin"
        query_get_announces = "SELECT idAnnounce, typeAnnounce, dateAnnounce, intitule, description, latitude, longitude, localisation, valid, idCat, idUser, catName, username, firstname, lastname FROM announce INNER JOIN category USING (idCat) INNER JOIN users USING (idUser) "
        if first_where and not select_unapproved_announces:
            first_where = False
            query_get_announces = query_get_announces + " WHERE (valid = 1 "
            if request.session.get("logged_user", False):
                query_get_announces = query_get_announces + " OR valid = 0 AND idUser = %s ) "
                values.append(request.session["idUser"])
            else:
                query_get_announces = query_get_announces + " ) "
        

        # recherche par critères
        if not default:
            check_search_input = self.check_search_input(request)
            if check_search_input[0]:
                search_params = check_search_input[1]
                if first_where:
                    query_get_announces = query_get_announces + " WHERE "
                else:
                    query_get_announces = query_get_announces + " AND "
                query_get_announces = query_get_announces + f" announce.idCat IN {misc.list_to_str_for_sql_queries(search_params['idCat'])} AND typeAnnounce IN {misc.list_to_str_for_sql_queries(search_params['types'])} AND dateAnnounce BETWEEN '{str(search_params['date1'])}' AND '{str(search_params['date2'])}' "
                if search_params['title'] != "":
                    query_get_announces = query_get_announces + f" AND intitule LIKE %s "
                    values.append(f"%{search_params['title']}%")
                if search_params['localisation'] != "":
                    if search_params['radius'] == 0:
                        query_get_announces = query_get_announces + f" AND localisation LIKE %s "
                        values.append(f"%{search_params['localisation']}%")
                    else:
                        query_get_announces = query_get_announces + f" AND latitude < {search_params['lat'] + (search_params['radius'] * self.COEFF_LATITUDE)} AND latitude > {search_params['lat'] - (search_params['radius'] * self.COEFF_LATITUDE)} AND longitude < {search_params['lon'] + (search_params['radius'] * self.COEFF_LONGITUDE)} AND longitude > {search_params['lon'] - (search_params['radius'] * self.COEFF_LONGITUDE)} "

        values = tuple(values)
        query_get_announces = query_get_announces + " ORDER BY dateAnnounce DESC "
        announces_list = self.mySqlConnector.execute_prepared_query(query_get_announces, values, True)
        if (search_params.get('radius', 0)>0):
            announces_list = self.filter_announces_by_radius(announces_list, search_params['radius'], search_params['localisation'])

        final_announces_list = []

        for announce in announces_list:
            final_announces_list.append({'idAnnounce':announce[0], 
                                             'typeAnnounce':announce[1], 
                                             'dateAnnounce':announce[2], 
                                             'intitule':announce[3], 
                                             'description':announce[4], 
                                             'latitude':announce[5], 
                                             'longitude':announce[6], 
                                             'localisation':ast.literal_eval(announce[7]), 
                                             'valid':announce[8], 
                                             'idCat':announce[9], 
                                             'idUser':announce[10], 
                                             'catName':announce[11], 
                                             'username':announce[12], 
                                             'firstname':announce[13], 
                                             'lastname':announce[14]})

        return {'announces':final_announces_list, 
                'starting_lat':search_params.get('lat',self.DEFAULT_LATITUDE),
                'starting_lon':search_params.get('lon',self.DEFAUT_LONGITUDE),
                'radius':search_params.get('radius', 0)
                }
    
    def filter_announces_by_radius(self, announces, radius, search_location):
        newlist = []
        search_loc_geocode = self.geolocator.geocode(search_location)
        for announce in announces:
            if geodesic( (search_loc_geocode.latitude, search_loc_geocode.longitude), (announce[5], announce[6]) ).kilometers <= radius:
                newlist.append(announce)
        
        return newlist

    def check_search_input(self,request):
        """
            vérifie si les données de la requête POST pour chercher des annonces
            sont conformes, les retourne si c'est le cas
        """

        search_params_ok = True
        lat = self.DEFAULT_LATITUDE
        lon = self.DEFAUT_LONGITUDE
        radius = 0

        try:
            # type
            announceTypes = []
            if request.POST.get("announceType1", 0) == "ok":
                announceTypes.append(1)
            if request.POST.get("announceType2", 0) == "ok":
                announceTypes.append(2)

            # localisation
            localisation = request.POST.get("announceLocation", "").strip()

            # les dates
            date_1 = datetime.strptime(request.POST.get("announceDate1", None), "%Y-%m-%d").date()
            date_2 = datetime.strptime(request.POST.get("announceDate2", None), "%Y-%m-%d").date()
            title = request.POST.get("announceTitle", "").strip()
            # rayon de recherche
            radius = request.POST.get("byRadius", 0)
            if (radius == "yes"):
                radius = int(request.POST.get("radius"))
                if radius > 500:
                    radius = 500
                elif radius < 0:
                    radius = 0

                if radius > 0:
                    # en cas de recherche par rayon, la localisation doit être géolocalisable
                    geoloca = self.geolocator.geocode(localisation)
                    lat = geoloca.latitude
                    lon = geoloca.longitude
            else:
                radius = 0

            ids_Cat = request.POST.getlist('categories[]') or []
            if len(ids_Cat)>0:
                ids_Cat = [int(idCat) for idCat in ids_Cat]

            search_params_ok = search_params_ok and all(self.is_category_id_valid(idCat) for idCat in ids_Cat)
        except Exception as e:
            search_params_ok = False
        
        if search_params_ok:
            search_dict = {'types':announceTypes, 'radius':radius, 'localisation':localisation, 'date1':date_1, 'date2':date_2, 'title':title, 'idCat':ids_Cat}
            if radius > 0:
                search_dict['lat'] = lat
                search_dict['lon'] = lon

            return (True, search_dict)
        else:
            return (False,)
    
    def check_new_announce_input(self, request):
        """
            vérifie si les données de la requête POST pour publier une nouvelle annonce
            sont conformes
        """

        """ 
            il faut être connecté et ne pas être banni pour pouvoir publier une annonce

            dans la requête POST, doivent être présents les clés suivantes
            announceType (valeur 1 ou 2 uniquement)
            announceLocation (un string que l'on donne à un geolocator : si il renvoie un None c'est qu'aucun endroit sur Terre ne correspond
            à la zone précisée => erreur)
            announceTitle (un string de longueur 200 max)
            announceCat (doit correspondre à un ID de catégorie connu dans la base de données)
            announceDescription (chaîne de caractères)
        """

        users = Users()

        is_announce_ok = request.session.get("logged_user", False)

        try:
            if (is_announce_ok):
                is_announce_ok = is_announce_ok and users.getLevel(request, request.session["login"]) != "banned"
                if (is_announce_ok):
                    announceType = int(request.POST.get("announceType", 0))
                    is_announce_ok = (announceType == 1 or announceType == 2)
                    if (is_announce_ok):
                        announceLocation = request.POST.get("announceLocation", "")
                        localisation = self.geolocator.geocode(announceLocation, addressdetails=True)
                        is_announce_ok = (localisation is not None)
                        if (is_announce_ok):
                            announceTitle = request.POST.get("announceTitle", "").strip()
                            is_announce_ok = (len(announceTitle) >= 10)
                            if (is_announce_ok):
                                idCat = int(request.POST.get("announceCat", ""))
                                is_announce_ok = self.is_category_id_valid(idCat)
        except:
            is_announce_ok = False

        if is_announce_ok:
            announceDescription = request.POST.get("announceDescription", "").strip()
            return (True, {'typeAnnounce':announceType, 'localisation':localisation.raw, 'intitule':announceTitle, 'idCat':idCat, 'description':announceDescription})
        else:
            return (False,)
    
    def edit_announce(self, request, idAnnounce):
        """
            modifie une annonce
        """
        success = False

        try:
            can_edit_query = f"SELECT idAnnounce FROM announce WHERE idUser = %s AND idAnnounce = %s"
            results = self.mySqlConnector.execute_prepared_query(can_edit_query, (request.session["idUser"], idAnnounce),True)
            can_edit = len(results)==1

            if can_edit:
                edit_announce_tuple = self.check_new_announce_input(request)
                if (edit_announce_tuple[0]):
                    edit_infos = edit_announce_tuple[1]
                    update_query = f"UPDATE announce SET typeAnnounce = %s, intitule = %s, description = %s, latitude = %s, longitude = %s, localisation = %s, valid = 0, idCat = %s WHERE idAnnounce = %s"
                    values = (edit_infos["typeAnnounce"], edit_infos["intitule"], f"[Modifié le {datetime.now().strftime("%d/%m/%Y")} à {datetime.now().strftime("%H:%M")}] - " + edit_infos["description"], edit_infos["localisation"]["lat"], edit_infos["localisation"]["lon"], str(edit_infos["localisation"]["address"]), edit_infos["idCat"], idAnnounce)
                    self.mySqlConnector.execute_prepared_query(update_query, values, False)
                    success = True
        except:
            pass

        return "L'annonce a été modifiée et devra être validée pour redevenir visible." if success else "L'annonce n'a pas pu être modifiée."


    
    def add_new_announce(self, request):
        """
            ajoute une nouvelle annonce dans la base de données.

            par défaut, elle n'est pas validée et doit être approuvée manuellement par l'admin
        """
        success = False

        new_announce_tuple = self.check_new_announce_input(request)
        if (new_announce_tuple[0]):
            insert_query = f"INSERT INTO announce (typeAnnounce, dateAnnounce, intitule, description, latitude, longitude, localisation, valid, idCat, idUser) VALUES (%s, current_date, %s, %s, %s, %s, %s, 0, %s, %s)"
            try:
                self.mySqlConnector.execute_prepared_query(insert_query, (new_announce_tuple[1]["typeAnnounce"], new_announce_tuple[1]["intitule"], new_announce_tuple[1]["description"], new_announce_tuple[1]["localisation"]["lat"], new_announce_tuple[1]["localisation"]["lon"], str(new_announce_tuple[1]["localisation"]["address"]), new_announce_tuple[1]["idCat"], request.session["idUser"]),False)
                success = True
            except:
                pass
            
        return success
    
    def moderate_announce(self, request, action, idAnnounce, level):
        """
            permet de modérer une annonce (valider ou supprimer)
        """
        users = Users()
        if (request.session.get("logged_user", False) and level == "admin"):
            if action == "validate" or action == "invalidate":
                valid_val = 1 if action == "validate" else 0
                validate_query = f"UPDATE announce SET valid = {valid_val} WHERE idAnnounce = %s"
                self.mySqlConnector.execute_prepared_query(validate_query, (idAnnounce,), False)

    def is_category_id_valid(self, idCat):
        query = f"SELECT idCat FROM category WHERE idCat = %s"
        result = self.mySqlConnector.execute_prepared_query(query, (idCat,),True)
        return len(result)==1
    
    def get_reviews(self, idAnnounce):
        """
            retourne les commentaires postés pour l'annonce d'id idAnnounce
        """
        results = self.mySqlConnector.execute_prepared_query(f"SELECT idReview, review.idUser, review.score, content, dateReview, idAnnounce, username, firstname, lastname FROM review INNER JOIN users USING (idUser) WHERE idAnnounce = %s ORDER BY dateReview DESC", (idAnnounce,), True)
        review_list = []
        for tupleReview in results:
            score_plus, score_minus = self.get_review_scores(tupleReview[0])
            review_list.append(Review(tupleReview, score_plus, score_minus))
        
        return review_list
    
    def new_review(self, request, idAnnounce, level):

        # être connecté, ne pas être banni, ne pas commenter sa propre annonce, ne pas avoir déjà commenté l'annonce, commentaire non vide, score entre 1 et 5

        return_msg = "Le commentaire n'a pas pu être ajouté. Vérifiez que vous avez bien respecté les règles."

        try:
            post_review = request.session.get("logged_user", False)
            if post_review:
                post_review = post_review and level != "banned"
                if post_review:
                    results = self.mySqlConnector.execute_prepared_query(f"SELECT idAnnounce FROM announce WHERE idUser = %s AND idAnnounce = %s", (request.session["idUser"], idAnnounce), True)
                    post_review = post_review and len(results) == 0
                    if post_review:
                        results = self.mySqlConnector.execute_prepared_query(f"SELECT idAnnounce FROM announce WHERE idAnnounce = %s AND valid = 1", (idAnnounce,), True)
                        post_review = post_review and len(results) == 1
                        if post_review:
                            has_user_already_reviewed = len(self.mySqlConnector.execute_prepared_query(f"SELECT idReview FROM review WHERE idUser = %s AND idAnnounce = %s", (request.session["idUser"], idAnnounce), True))>0
                            post_review = post_review and not has_user_already_reviewed
                            if post_review:
                                comment = request.POST.get("reviewContent", "").strip()
                                post_review = post_review and len(comment)>0
                                if post_review:
                                    score = int(request.POST.get("rate", 0))
                                    post_review = post_review and score >= 1 and score <= 5
                                    if post_review:
                                        insert_review_query = f"INSERT INTO review (idUser, score, content, dateReview, idAnnounce) VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)"
                                        values = (request.session["idUser"], score, comment, idAnnounce)
                                        self.mySqlConnector.execute_prepared_query(insert_review_query, values, False)
                                        return_msg = "Le commentaire a été ajouté."
        except:
            pass

        return return_msg
    
    def remove_announce(self, idAnnounce, is_owner_current_user, level):
        # il faut être propriétaire de l'annonce ou admin pour la supprimer
        return_val = (1, "Vous n'avez pas le droit de supprimer cette annonce.")
        can_remove = is_owner_current_user or level == "admin"
        if (can_remove):
            get_reviews_query = f"SELECT idReview FROM review WHERE idAnnounce = %s"
            values = (idAnnounce,)
            try:
                f = open("debug.txt", "a")
                reviews_id = self.mySqlConnector.execute_prepared_query(get_reviews_query, values, True)
                reviews_id_to_delete = []
                for review_tuple in reviews_id:
                    reviews_id_to_delete.append(review_tuple[0])
                
                if len(reviews_id_to_delete)>0:
                    remove_query = f"DELETE FROM reviewRating WHERE idReview IN {repr(tuple(reviews_id_to_delete))}"
                    self.mySqlConnector.execute_prepared_query(remove_query, review_tuple, False)
                    remove_query = f"DELETE FROM review WHERE idAnnounce = %s"
                    self.mySqlConnector.execute_prepared_query(remove_query, values, False)

                remove_query = f"DELETE FROM announce WHERE idAnnounce = %s"
                self.mySqlConnector.execute_prepared_query(remove_query, values, False)

                return_val = (0, "L'annonce a bien été supprimée.")
            except Exception as e:
                f.write(f"{repr(e)}\n")
                f.close()
                return_val = (1, "Une erreur imprévue est survenue.")
        
        return return_val
    
    def get_score(self, idAnnounce):
        # moyenne des reviews
        query = f"SELECT avg(score) FROM review INNER JOIN users USING (idUser) WHERE privilegeLevel > 0 AND idAnnounce = %s"
        average = self.mySqlConnector.execute_prepared_query(query, (idAnnounce,), True)[0][0]
        try:
            average = float(average)
            context_average = round(average)
        except:
            average = 0.0
            context_average = 0
        
        return (average, context_average)
    
    def has_user_already_commented(self, idAnnounce, idUser):
        query = f"SELECT * FROM review WHERE idAnnounce = %s AND idUser = %s"
        values = (idAnnounce, idUser)
        has_commented = False
        try:
            has_commented = len(self.mySqlConnector.execute_prepared_query(query, values, True))>0
        except:
            pass

        return has_commented
    
    def get_review_scores(self, idReview):
        """
            retourne les scores d'un commentaire (plus et moins)
        """
        query_plus = f"SELECT count(idReviewRating) FROM reviewrating WHERE idReview = %s AND rating = 1"
        query_minus = f"SELECT count(idReviewRating) FROM reviewrating WHERE idReview = %s AND rating = -1"
        
        try:
            score_plus = self.mySqlConnector.execute_prepared_query(query_plus, (idReview,), True)[0][0]
        except:
            score_plus = 0
        
        try:
            score_minus = self.mySqlConnector.execute_prepared_query(query_minus, (idReview,), True)[0][0]
        except:
            score_minus = 0
        
        return score_plus, score_minus

    
    def rate_review(self, request, idReview, idUser, rating, username):
        users = Users()
        final_ok = False
        score_plus = 0
        score_minus = 0

        try:
            ok = users.getLevel(request, username) != "banned"
            query_is_own_review = f"SELECT idReview FROM review WHERE idReview = %s AND idUser = %s"
            if ok:
                ok = len(self.mySqlConnector.execute_prepared_query(query_is_own_review, (idReview, idUser), True))==0
                if ok:
                    query = f"SELECT rating FROM reviewrating WHERE idUser = %s and idReview = %s"
                    results = self.mySqlConnector.execute_prepared_query(query, (idUser, idReview), True)
                    if len(results)>0:
                        if rating != results[0][0]:
                            query = f"UPDATE reviewrating SET rating = %s WHERE idReview = %s AND idUser = %s"
                            self.mySqlConnector.execute_prepared_query(query, (rating, idReview, idUser), False)
                            final_ok = True
                        else:
                            query = f"DELETE FROM reviewrating WHERE idUser = %s and idReview = %s"
                            self.mySqlConnector.execute_prepared_query(query, (idUser, idReview), False)
                            final_ok = True
                    else:
                        query = f"INSERT INTO reviewrating (idReview, rating, idUser) VALUES (%s, %s, %s)"
                        self.mySqlConnector.execute_prepared_query(query, (idReview, rating, idUser), False)
                        final_ok = True
        except:
            pass
            
        if final_ok:
            score_plus, score_minus = self.get_review_scores(idReview)

        return {'ok':final_ok, 'score_plus':score_plus, 'score_minus':score_minus, 'idDivScorePlus':f'scorePlus_{idReview}', 'idDivScoreMinus':f'scoreMinus_{idReview}'}
