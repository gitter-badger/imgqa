# -*- coding: utf-8 -*-
"""Comparison Module for Images, Files like CSV, Excel, PDF etc."""
import os
import sys
import unittest
import collections
import pandas as pd
import cv2
from skimage.measure import compare_ssim as ssim
import numpy as np
import json
from simplejson import JSONDecodeError
from matplotlib import pyplot as plt
import logging


class CompareFiles(unittest.TestCase):
    """File Comparison module which includes image, csv and workbook."""

    def __compare_image_structure(self, source_image, target_image):
        """Checkpoint 1 to measure on size and shape of image.

        :param source_image: source image
        :param target_image: target image
        :return: returns boolean value based on images structure similarity
        :rtype: boolean value.
        """
        if source_image.shape == target_image.shape:
            logging.info("Images of same size")
            difference = cv2.subtract(source_image, target_image)
            b, g, r = cv2.split(difference)
            if cv2.countNonZero(b) == cv2.countNonZero(g) == cv2.countNonZero(r) == 0:
                logging.info("The images are completely Equal")
                return True
            else:
                logging.warning("RGB Attributes are different though images are same size")
                return False
        else:
            logging.warning("The images have different size and channels")
            return False

    def __compare_images_mse(self, source_image, target_image):
        """Checkpoint to measure on size and shape of image.

        :param source_image:
        :param target_image:
        :return: returns boolean value based on images mse values
        :rtype: boolean value

        """
        mse_val = np.sum((source_image.astype("float") - target_image.astype("float")) ** 2)
        mse_val /= float(source_image.shape[0] * source_image.shape[1])

        if mse_val == 0.00:
            return True
        elif mse_val > 0:
            logging.warning("Images MSE value: %s" % mse_val)
            return False

    def __compare_images_ssim(self, source_image, target_image):
        pass

    def compare_images(self, source_img, target_img):
        """Compare two images on the basis mse and ssim index.

        :param source_img: source image.
        :param target_img: target image.
        :return: list of boolean value of image comparision,
        mse value and ssim value.
        """
        # list of expected image extensions
        extn = ('jpg', 'jpeg', "png")
        if source_img.split(".") not in extn and target_img.split(".") not in extn:
            logging.error("Invalid image file extention")
            return False

        source = cv2.imread(source_img)
        target = cv2.imread(target_img)
        if self.__compare_image_structure(source, target) \
            and self.__compare_image_mse(source, target) \
            and self.__compare_image_ssim(source, target):
            logging.info("The images are perfectly similar")
            return True
        else:
            logging.warning("The images are not similar")


    images_equal = False
    images_same_size_channel = False
    mse_ssim_equality = True
    width = 2160

    def compare_images(self, imgpath1, imgpath2):
        """Compare two images on the basis mse and ssim index.

        :param imgpath1: Path for the first image file to compare.
        :param imgpath2: Path for the second image file to compare.
        :return: list containing True/False depending on the
        images similarity, mse value and ssim value.
        :rtype: list
        """
        try:
            image1_extenion = imgpath1.split(".")[1]
            image2_extension = imgpath2.split(".")[1]

            if image1_extenion not in ('jpg', 'jpeg', 'png') \
                    and image2_extension not in \
                    ('jpg', 'jpeg', 'png'):
                logging.warning("Invalid image extension.")

            else:
                load_img1 = cv2.imread(imgpath1)
                load_img2 = cv2.imread(imgpath2)

                # resize image2 by keeping original height
                dim = (self.width, load_img2.shape[0])
                resize_image = cv2.resize(load_img2, dim, interpolation=cv2.INTER_AREA)

                # Convert an image color to gary
                img1_grayscale = cv2.cvtColor(load_img1, cv2.COLOR_BGR2GRAY)
                img2_grayscale = cv2.cvtColor(resize_image, cv2.COLOR_BGR2GRAY)

                # Uncomment the following code if you want to use matplot
                # lib to see the image difference.
                # self._comparing_images_visually_thru_matplotlib(img1_grayscale,
                #                                                 img2_grayscale)

                # compare the images
                dict_img_compare = self.__mse_ssim_comparison(img1_grayscale,
                                                             img2_grayscale)
                cv_compare_val = self.__image_compare_thru_opencv(
                    imgpath1,
                    imgpath2)
                dict_img_compare.append(cv_compare_val)
                return dict_img_compare
        except Exception:
            logging.warning("There is some issue in image comparison.")

    def __image_compare_thru_opencv(self, first_image, second_image):
        """Compare two images using OpenCV library, on the basis of their shapes.

        and b, g, r channels and return True/False depending on whether the
         two images are same or not.
        :param first_image_path: Path for the first image file to compare.
        :param second_image_path: Path for the second image file to compare.
        :return: True/False depending upon whether both images are same or not.
        :rtype: boolean
        """
        try:
            first_image_extenion = first_image.split(".")[1]
            second_image_extension = second_image.split(".")[1]

            if first_image_extenion not in ('jpg', 'jpeg', 'png') and \
                    second_image_extension not in ('jpg', 'jpeg', 'png'):
                logging.warning("Invalid image extension.")
            # Reading the image files
            else:
                img1 = cv2.imread(first_image)
                img2 = cv2.imread(second_image)

                # keep original height
                height = img2.shape[0]
                dim = (self.width, height)

                # resizing image2
                resized_img2 = cv2.resize(img2, dim, interpolation=cv2.INTER_AREA)

                if img1.shape == img2.shape:
                    images_same_size_channel = True
                    difference = cv2.subtract(img1, resized_img2)

                    b, g, r = cv2.split(difference)
                    if cv2.countNonZero(b) == 0 and cv2.countNonZero(g) == 0 \
                            and cv2.countNonZero(r) == 0:
                        images_equal = True
                    else:
                        images_equal = False

                else:
                    images_same_size_channel = False

                # Following is to close the open windows for any analysis
                # presentation. Mostly unsued while running through CLI.
                # self._visual_difference(difference)

                if images_same_size_channel is True and images_equal is True:
                    return True
                else:
                    return False
        except Exception:
            logging.warning("There is some issue in image comparison.")

    def _visual_difference(self, difference):
        """Shows the difference between 2 images.

        :param difference: CV2 difference between 2 images
        :return: NA
        :rtype: NA
        """
        try:
            cv2.imshow("difference", difference)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        except Exception:
            logging.warning("There is some issue in _visual_difference "
                            "method.")

    def __mse(self, img1, img2):
        """Calculate the mse error between the 2 images.

        :param img1: First image to compare.
        :param img2: Second image to compare.
        :return: mse error value between 2 images.
        :rtype: float number
        """
        try:
            # the 'MSE(Mean Squared Error)' between the two images is the
            # sum of the squared difference between the two images;
            # NOTE: the two images must have the same dimension
            err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
            err /= float(img1.shape[0] * img1.shape[1])

            # return the MSE, the lower the error, the more "similar"
            # the two images are
            return err
        except Exception:
            logging.warning("There is some issue in mse "
                            "calculation of 2 images.")

    def __mse_ssim_comparison(self, img1, img2):
        """Calculate mse and ssim values for the images provided.

        :param img1: First image to compare.
        :param img2: Second image to compare.
        :return: dictionary containing mse, ssim values and
        True/False depending on the equlaity of images.
        :rtype: dictionary
        """
        mse_sssim_vals = []

        """SSIM and Mean Squared Error Comparison."""
        try:
            # compute the mean squared error and structural similarity
            # index for the images
            mse_val = self.__mse(img1, img2)
            ssim_val = ssim(img1, img2)

            if mse_val == 0.00 and ssim_val == 1.00:
                mse_ssim_equality = True
                mse_sssim_vals.append(mse_ssim_equality)
            elif mse_val > 0 and ssim_val < 1:
                mse_ssim_equality = False
                mse_sssim_vals.append(mse_ssim_equality)
                mse_sssim_vals.append(mse_val)
                mse_sssim_vals.append(ssim_val)

            # Uncomment the following code if you want to use matplot
            # lib to see the image difference.
            # self._image_difference_thru_matplotlib\
            #     (mse_val,ssim_val, img1, img2, "first vd second")

            return mse_sssim_vals
        except Exception:
            logging.warning("Image's mse and ssim are not same.")

    def _image_difference_thru_matplotlib(self, mse_val, ssim_val, img1, img2, title):
        """Provide configuration for displaying images through matplot lib.

        along with their mse and ssim values.
        :param mse_val: mse index value of the 2 images.
        :param ssim_val: ssim index value of the 2 images.
        :param img1: First image to compare.
        :param img2: Second image to compare.
        :param title: Title for comparison to be shown through matplot lib.
        :return: NA
        :rtype: NA
        """
        try:
            # setup the figure
            fig = plt.figure(title)
            plt.suptitle("MSE: %.2f, SSIM: %.2f" % (mse_val, ssim_val))

            # show first image
            fig.add_subplot(1, 2, 1)
            plt.imshow(img1, cmap=plt.cm.gray)
            plt.axis("off")

            # show the second image
            fig.add_subplot(1, 2, 2)
            plt.imshow(img2, cmap=plt.cm.gray)
            plt.axis("off")

            # show the images
            plt.show()
        except Exception:
            logging.warning("There is some issue in "
                            "_image_difference_thru_matplotlib method.")

    def _comparing_images_visually_thru_matplotlib(self, first_img, second_img):
        """Displays the 2 images using matplotlib along with.
         their mse and ssim values.
        :param first_img: First image to compare.
        :param second_img: Second image to compare.
        :return: NA
        :rtype: NA
        """
        try:
            fig = plt.figure("Images")
            images = ("First", first_img), ("Second", second_img)
            for (i, (name, image)) in enumerate(images):
                # show the image
                ax = fig.add_subplot(1, 3, i + 1)
                ax.set_title(name)
                plt.imshow(image, cmap=plt.cm.gray)
                plt.axis("off")

            # show the figure
            plt.show()
        except Exception:
            logging.warning("There is some issue in "
                            "_comparing_images_visually_thru_matplotlib "
                            "method.")

    def compare_json(self, first_json, second_json):
        """Compare two jsons and generates a text file containing the.

            difference.
        :param first_json_path: Path for the first json file to compare.
        :param second_json_path: Path for the second json file to compare.
        :return: True/False depending upon whether both jsons are same or not.
        :rtype: boolean
        """

        try:
            first_json_extenion = first_json.split(".")[1]
            second_json_extension = second_json.split(".")[1]
            if first_json_extenion != 'json' and \
                    second_json_extension != 'json':
                logging.warning("Please provide correct file extensions "
                                "for json comparison.")
            # Reading the json files
            else:
                # Reading the jsons and converting them into dictionaries.
                with open(first_json) as first_json:
                    dict1 = json.load(first_json)
                with open(second_json) as second_json:
                    dict2 = json.load(second_json)

                boolean_json_diff = self.write_json_diff_to_file(dict1, dict2)
            return boolean_json_diff

        except JSONDecodeError:
            logging.warning("Invalid json. Please provide file with proper"
                            " json structure.")
        except Exception:
            logging.warning("There is some issue in json comparison.")

    def write_json_diff_to_file(self, dict1, dict2, path=""):
        """Compare two json and writes the difference to a file.

        :param dict1: first dictionary to compare.
        :param dict2: second dictionary to compare.
        :return: True/False depending upon whether both jsons are same or not.
        :rtype: boolean
        """
        are_json_different = False
        try:
            # Sorting the dictionaries.
            sorted_dict1 = collections.OrderedDict(sorted(dict1.items()))
            sorted_dict2 = collections.OrderedDict(sorted(dict2.items()))
            if path is "":
                try:
                    os.remove("json_diff.txt")
                except OSError:
                    pass

            # Checking whether both json objects are instances of dict.
            if isinstance(dict1, dict) and isinstance(dict2, dict):
                # Checking whether length of both dictionaries is same.
                if len(dict1) == len(dict2):
                    # Checking if the keys are matching in both
                    # dictionaries.
                    if sorted_dict1.keys() == sorted_dict2.keys():
                        for k in dict1.keys():
                            # Checking whether some key present in one
                            # dictionary is not present in
                            # other dictionary.
                            if k not in dict2.keys():
                                keydiff = (str(k) +
                                           " as key not in d2")
                                with open('json_diff.txt', 'a') \
                                        as the_file:
                                    the_file.write(str(keydiff))
                            else:
                                if type(dict1[k]) is dict:
                                    if path == "":
                                        path = k
                                    else:
                                        path = path + "->" + k
                                    # Making recursive call by passing
                                    # the keys which are present
                                    # as dictionary object.
                                    self.write_json_diff_to_file(dict1[k],
                                                                 dict2[k],
                                                                 path)
                                else:
                                    if dict1[k] != dict2[k]:
                                        are_json_different = True
                                        keystr = (str(path), ":")
                                        first_file_val = " First file ", \
                                                         k, " : ", dict1[k]
                                        second_file_val = " Second file ",\
                                                          k, " : ", dict2[k]

                                        # Writing the difference to
                                        # the file.
                                        with open('json_diff.txt', 'a') \
                                                as the_file:
                                            the_file.write(str(keystr)
                                                           + '\n')
                                            the_file.write(str(first_file_val)
                                                           + '\n')
                                            the_file.write(str(second_file_val)
                                                           + '\n')
                                            the_file.write('\n')
                    else:
                        logging.warning("Keys are different in "
                                        "both dictionaries.")
                else:
                    logging.warning("Length of both dictionaries"
                                    " is different.")

            return are_json_different
        except JSONDecodeError:
            logging.warning("Invalid json. Please provide file with proper"
                            " json structure.")
        except Exception:
            logging.warning("There is some issue in json comparison.")

    def compare_spreadsheet(self, first_sheet, second_sheet):
        """Compare two spreadsheets and generates an excel file containing the.

        difference. If resultant excel file contain empty cell that means
        the value is same in both excels else not.
        :param first_sheet: Path for the first sheet to compare.
        :param second_sheet: Path for the second sheet to compare.
        :return: True/False depending upon whether both sheets are same or not.
        :rtype: boolean
        """
        are_sheets_different = True
        try:
            first_sheet_extension = first_sheet.split(".")[1]
            second_sheet_extension = second_sheet.split(".")[1]
            if first_sheet_extension not in ('xls', 'xlsx', 'csv') and \
                    second_sheet_extension not in ('xls', 'xlsx', 'csv'):
                logging.warning("Please provide correct file "
                                "extensions for spreadsheet comparison.")
            # Reading the excel files
            else:
                if first_sheet_extension in ('csv') and \
                        second_sheet_extension in ('csv'):
                    writer = pd.ExcelWriter(
                        'csv_excel1.xlsx', engine='xlsxwriter')
                    pd.read_csv(first_sheet).\
                        to_excel(writer,
                                 sheet_name='sheet1',
                                 index=False,
                                 encoding=sys.getfilesystemencoding()
                                 )
                    writer = pd.ExcelWriter(
                        'csv_excel2.xlsx', engine='xlsxwriter')
                    pd.read_csv(second_sheet).\
                        to_excel(writer,
                                 sheet_name='sheet1',
                                 index=False,
                                 encoding=sys.getfilesystemencoding()
                                 )
                    excel1 = pd.read_excel('csv_excel1.xlsx',
                                           encoding=sys.getfilesystemencoding()
                                           )
                    excel2 = pd.read_excel('csv_excel2.xlsx',
                                           encoding=sys.getfilesystemencoding()
                                           )
                else:
                    excel1 = pd.read_excel(first_sheet,
                                           encoding=sys.getfilesystemencoding()
                                           )
                    excel2 = pd.read_excel(second_sheet,
                                           encoding=sys.getfilesystemencoding()
                                           )

                # Checking if the excels are empty
                if excel1.empty is True and excel2.empty is True:
                    logging.warning("The excel files are empty")

                # Checking whether the no.of rows is same in both excels.
                elif len(excel1) != len(excel2):
                    logging.warning("The no. of rows in both "
                                    "excel are not same")

                # Checking whether the no.of columns is same in both excels.
                elif len(excel1.columns) != len(excel2.columns):
                    logging.warning("The no. of columns in both "
                                    "excel are not same")
                else:
                    # Setting column order same in both excels.
                    excel1.columns = excel2.columns

                    # Sorting excel data on the basis of a column.
                    try:
                        excel1 = excel1.sort_values(
                            'id', ascending=False).reset_index(inplace=False)
                        excel2 = excel2.sort_values(
                            'id', ascending=False).reset_index(inplace=False)
                    except Exception:
                        pass

                    # Getting the difference in data between both excels.
                    difference = excel1[excel1 != excel2]
                    if (difference.isnull().values.all()) is True:
                        are_sheets_different = False

                    # Writing the delta between both excels in a separate
                    # excel file.
                    writer = pd.ExcelWriter(
                        'excel_diff.xlsx', engine='xlsxwriter')
                    difference.to_excel(writer,
                                        sheet_name='sheet1',
                                        index=False,
                                        encoding=sys.getfilesystemencoding())
            return are_sheets_different
        except Exception:
            logging.warning("There is some issue in spreadsheet comparison.")