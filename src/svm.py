"""
svm.py
Trains a Support Vector Machine to perform subcellular location prediction
Author: Ramon Viñas, 2018
Contact: ramon.torne.17@ucl.ac.uk
"""
from sklearn.svm import SVC
from data_pipeline import get_handcrafted_data
from sklearn.model_selection import cross_val_score
import numpy as np
from utils import get_test_split, get_val_split, plot_confusion_matrix, plot_roc_curve
from sklearn.metrics import f1_score

do = 'cv'

x, y, x_blind, info_blind, class_dict = get_handcrafted_data()
class_dict_inv = {i: c for c, i in class_dict.items()}
model = SVC(C=40, probability=True)  # random_state=0 , class_weight='balanced'
if do == 'blind':
    model.fit(x, y)
    probs = model.predict_proba(x_blind)
    am = np.argmax(probs, axis=-1)
    for id, p, a in zip(info_blind, probs, am):
        print('{} & {} & {:.2f} \\\\'.format(id.rstrip().replace('>', ''), class_dict_inv[a], p[a]))
else:
    train_idxs, test_idxs = get_test_split(y)
    x_train, y_train = x[train_idxs, :], y[train_idxs]
    x_test, y_test = x[test_idxs, :], y[test_idxs]
    print('Training examples: {}'.format(len(train_idxs)))
    print('Testing examples: {}'.format(len(test_idxs)))

    if do == 'cv':
        cv_score = cross_val_score(model, x_train, y_train, cv=4, scoring='f1_micro')  # f1_micro
        print('CV score. Mean: {}. Sd: {}'.format(np.mean(cv_score), np.std(cv_score)))

        cs = []
        scores = []
        for c in np.random.uniform(1, 50, 50):
            model = SVC(C=c)  # , probability=True
            cv_score = cross_val_score(model, x_train, y_train, cv=4, scoring='f1_micro')
            cs.append(c)
            scores.append(np.mean(cv_score))
            print('C: {}. CV score. Mean: {}. Sd: {}'.format(c, np.mean(cv_score), np.std(cv_score)))
        print(list(zip(cs, cv_score)))
    elif do == 'test':
        model.fit(x_train, y_train)
        test_score = model.score(x_test, y_test)
        print('Test score: {}'.format(test_score))

        class_dict_inv = {v: k for k, v in class_dict.items()}
        y_pred = model.predict(x_test)
        f1s = f1_score(y_test, y_pred, average=None)
        print('F1 scores:')
        for k, i in class_dict.items():
            print('{}: {}'.format(k, f1s[i]))
        plot_confusion_matrix(y_pred, y_test, [class_dict_inv[i] for i in range(len(class_dict))], normalize=True)
        y_pred = model.predict_proba(x_test)
        plot_roc_curve(y_pred, y_test, class_dict)
