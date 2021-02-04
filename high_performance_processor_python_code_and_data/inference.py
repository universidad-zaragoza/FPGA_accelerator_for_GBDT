#!/usr/bin/env python2
# -*- coding: utf-8 -*-
from __future__ import division, absolute_import, print_function
import os
import timeit
import scipy.io
import numpy as np
import joblib

# Images information
IMAGES = {
    "indian_pines": {
        "file": "Indian_pines_corrected.mat",
        "file_gt": "Indian_pines_gt.mat",
        "key": "indian_pines_corrected",
        "key_gt": "indian_pines_gt",
        "url": "http://www.ehu.eus/ccwintco/uploads/6/67/Indian_pines_corrected.mat",
        "url_gt": "http://www.ehu.eus/ccwintco/uploads/c/c4/Indian_pines_gt.mat",
        "p": 0.15
    },
    "KSC": {
        "file": "KSC.mat",
        "file_gt": "KSC_gt.mat",
        "key": "KSC",
        "key_gt": "KSC_gt",
        "url": "http://www.ehu.es/ccwintco/uploads/2/26/KSC.mat",
        "url_gt": "http://www.ehu.es/ccwintco/uploads/a/a6/KSC_gt.mat",
        "p": 0.15
    },
    "paviaU": {
        "file": "PaviaU.mat",
        "file_gt": "PaviaU_gt.mat",
        "key": "paviaU",
        "key_gt": "paviaU_gt",
        "url": "http://www.ehu.eus/ccwintco/uploads/e/ee/PaviaU.mat",
        "url_gt": "http://www.ehu.eus/ccwintco/uploads/5/50/PaviaU_gt.mat",
        "p": 0.15
    },
    "salinas": {
        "file": "Salinas.mat",
        "file_gt": "Salinas_gt.mat",
        "key": "salinas",
        "key_gt": "salinas_gt",
        "url": "http://www.ehu.eus/ccwintco/uploads/f/f1/Salinas.mat",
        "url_gt": "http://www.ehu.eus/ccwintco/uploads/f/fa/Salinas_gt.mat",
        "p": 0.15
    }
}

# PREPROCESSING FUNCTIONS
# =============================================================================

def load_image(image_info, data_path="."):
    """Loads the image and the ground truth from a `mat` file.
    
    If the file is not present in the `data_path` directory, downloads
    the file from the `image_info` url.
    
    Parameters
    ----------
    image_info: dict
        Dict structure with information of the image.
    data_path: str, optional (default ".")
        Absolute route of the directory of the image files.
    
    Returns
    -------
    X: NumPy array
        The loaded image data.
    y: NumPy array
        The loaded ground truth data.
    
    """
    # Image name
    image_name = image_info['key']
    
    # Filenames
    input_file = os.path.join(data_path, image_info['file'])
    label_file = os.path.join(data_path, image_info['file_gt'])
    
    # LOAD IMAGE
    try:
        
        # Load image file
        X = scipy.io.loadmat(input_file)[image_name]
    
    except:
        
        # Download image file
        os.system("wget {} -O {}".format(image_info['url'], input_file))
	    
	    # Load image file
        X = scipy.io.loadmat(input_file)[image_name]
    
    # LOAD GROUND TRUTH
    try:
        
        # Load ground truth file
        y = scipy.io.loadmat(label_file)[image_info['key_gt']]
    
    except:
        
        # Download ground truth file
        os.system("wget {} -O {}".format(image_info['url_gt'], label_file))
	    
	    # Load ground truth file
        y = scipy.io.loadmat(label_file)[image_info['key_gt']]
    
    return X, y

def pixel_classification_preprocessing(X, y):
    """Preprocesses hyperspectral images for pixel classification.
    
    Reshapes the image and the ground truth data, keeps only the labeled
    pixels and renames the classes to ordered integers from 0.
    
    Parameters
    ----------
    X: NumPy array
        The image data.
    y: NumPy array
        The ground truth data.
    
    Returns
    -------
    X: NumPy array
        The prepreocessed pixels.
    y: NumPy array
        The prepreocessed labels.
    
    """
    # Reshape them to ignore spatiality
    X = X.reshape(-1, X.shape[2])
    y = y.reshape(-1)
    
    # Keep only labeled pixels
    X = X[y > 0, :]
    y = y[y > 0]
    
    # Rename clases to ordered integers from 0
    for new_class_num, old_class_num in enumerate(np.unique(y)):
        y[y == old_class_num] = new_class_num
    
    return X, y

def random_index(X, y, seed=69):
  assert len(X) == len(y)
  return np.random.RandomState(seed=seed).permutation(len(X))

def separate_pixels(X, y, p):
    """Separate pixels and labels into train and test sets.
    
    Input data has to be preprocessed so classes are consecutively
    named from '0'.
    
    Parameters
    ----------
    X: NumPy array
        The preprocessed pixels.
    y: NumPy array
        The preprocessed labels.
    p: float
        The percentage of training pixels.
    
    Returns
    -------
    X_train: NumPy array
        Structure corresponding to the train pixels.
    y_train: NumPy array
        Structure corresponding to the train labels.
    X_test: NumPy array
        Structure corresponding to the test pixels.
    y_test: NumPy array, NumPy array, NumPy array)
        Structure corresponding to the test labels.
    
    """
    # Shuffle input data
    index = random_index(X, y)
    X = X[index]
    y = y[index]
    
    # Get the number of pixels for each class
    pixels = np.unique(y, return_counts=True)[1]
    
    # Generate the data sets sizes
    train_pixels = [int(n*p) for n in pixels]
    train_pixels = [1 if n == 0 else n for n in train_pixels]
    test_pixels = [a - b for a, b in zip(pixels, train_pixels)]
    
    # Calculate sizes of each structure
    num_train_pixels = sum(train_pixels)
    num_test_pixels = sum(test_pixels)
    
    # Shape of each pixel (some models use complex structures for spaciality)
    pixel_shape = X.shape[1:]
    
    # Prepare structures for train  and test data
    X_train = np.zeros((num_train_pixels,) + pixel_shape)
    y_train = np.zeros((num_train_pixels,), dtype=int)
    X_test = np.zeros((num_test_pixels,) + pixel_shape)
    y_test = np.zeros((num_test_pixels,), dtype=int)
    
    # Fill train and test data structures
    train_end = 0
    test_end = 0
    for class_num, (num_train_pixels_class,
                    num_test_pixels_class) in enumerate(zip(train_pixels,
                                                            test_pixels)):
        
        # Get instances of class `class_num`
        class_data = X[y == class_num, :]
        class_labels = y[y == class_num]
        
        # Save train pixels
        train_start = train_end
        train_end = train_start + num_train_pixels_class
        class_start = 0
        class_end = num_train_pixels_class
        X_train[train_start:train_end] = class_data[class_start:class_end]
        y_train[train_start:train_end] = class_labels[class_start:class_end]
        
        # Save test pixels
        test_start = test_end
        test_end = test_start + num_test_pixels_class
        class_start = class_end
        class_end = class_end + num_test_pixels_class
        X_test[test_start:test_end] = class_data[class_start:class_end]
        y_test[test_start:test_end] = class_labels[class_start:class_end]
    
    # Shuffle train data
    index = random_index(X_train, y_train)
    X_train = X_train[index]
    y_train = y_train[index]
    
    return X_train, y_train, X_test, y_test

# INFERENCE FUNCTIONS
# =============================================================================

def lightgbm_predict(trained_model, X_test, y_test, num_iter=200,
                     power_measurement_iterations=0):
    """Predicts the test evaluation data of the LightGBM model.
    
    Parameters
    ----------
    trained_model:
        The LightGBM trained model.
    X_test: NumPy array
        The test pixels.
    y_test: NumPy array
        The test labels.
    num_iter: int, optional (default 200)
        The `num_iteration` LightGBM parameter that corresponds with the
        number of trees used for each class.
    power_measurement_iterations: int, optional (default 0)
        The number of prediction iterations to perform. This is used to
        increase the time in order to measure power consumption.
    
    Returns
    -------
    time: float
        The computational time of the prediction in seconds.
    speed: int
        The number of pixels predicted per second.
    accuracy: float
        The Top 1 accuracy achieved.
    
    """
    if power_measurement_iterations > 0:
        
        print("--- START ---") # Now you can start measuring power consumption
        
        # Predict with test data and get time
        start_time = timeit.default_timer()
        for i in range(power_measurement_iterations):
            test_pred = trained_model.predict(X_test, num_iteration=num_iter)
        end_time = timeit.default_timer()
        time = end_time - start_time
        speed = int(X_test.shape[0] * power_measurement_iterations / time)
    
    else:
        
        # Predict with test data and get time
        start_time = timeit.default_timer()
        test_pred = trained_model.predict(X_test, num_iteration=num_iter)
        end_time = timeit.default_timer()
        time = end_time - start_time
        speed = int(X_test.shape[0] / time)
    
    # Get accuracy
    test_ok = (test_pred == y_test)
    accuracy = test_ok.sum() / test_ok.size
    
    return time, speed, accuracy

# MAIN FUNCTION
# =============================================================================

def main():
    
    # For each image
    for img in IMAGES:
        
        # Get image information
        image_info = IMAGES[img]
        image_name = image_info["key"]
        train_size = image_info["p"]
        
        print("\n{}".format(image_name))
        
        # Load image
        X, y = load_image(image_info)
        
        # Preprocess image
        X, y = pixel_classification_preprocessing(X, y)
        
        # Get test pixels
        _, _, X_test, y_test = separate_pixels(X, y, train_size)
        
        # Load model
        model = joblib.load("{}_model.joblib".format(image_name))
        
        # Perform inference
        time, speed, accuracy = lightgbm_predict(model, X_test, y_test)
        
        print("Prediction time: {:.3f}s ({}px/s)".format(time, speed))
        print("Test Accuracy:   {:.3f}\n".format(accuracy))

if __name__ == "__main__":
    main()

