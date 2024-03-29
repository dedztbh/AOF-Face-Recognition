import math
from os import path

from sklearn import neighbors
import time

from util.file import load
from util.predictor import EncodingsPredictor, get_param, get_param_default


def knn_generate(X, y, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    start = time.time()
    lenX = len(X)
    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(lenX)))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, y)

    print('Trained KNN model with {} training sets in {:.3f}ms'.format(lenX, (time.time() - start) * 1000))
    return knn_clf


def predict(X_encodings, knn_clf, distance_threshold=0.6, n_neighbors=1, print_time=True):
    if print_time:
        start = time.time()
    # if knn_clf is None:
    #     raise Exception("Must supply knn classifier")

    # If no faces are found in the image, return an empty result.
    if len(X_encodings) == 0:
        return []

    lenX = len(X_encodings)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(X_encodings, n_neighbors=n_neighbors)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(lenX)]

    if print_time:
        print('Made {} predictions in {:.3f}ms'.format(lenX, (time.time() - start) * 1000))

    # Predict classes and remove classifications that aren't within the threshold
    return [pred if rec else "Unknown" for pred, rec in
            zip(knn_clf.predict(X_encodings), are_matches)]


class KNNPredictor(EncodingsPredictor):
    def __init__(self, **kwargs):
        self.knn_trained = load(
            filename=get_param('model_name', kwargs),
            folder=path.join('data', 'model', 'knn'))
        self.n = get_param('n', kwargs)
        self.tolerance = get_param_default('tolerance', 0.54, kwargs)
        self.print_time = get_param_default('print_time', False, kwargs)

    def predict(self, face_encodings):
        return predict(X_encodings=face_encodings,
                       knn_clf=self.knn_trained,
                       distance_threshold=self.tolerance,
                       n_neighbors=self.n,
                       print_time=self.print_time)
