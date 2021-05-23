import cv2
import operator
import numpy as np
from matplotlib import pyplot as plt
from tensorflow.keras.models import load_model
from keras.models import model_from_json
from skimage.segmentation import clear_border

def plot_many_images(images, titles, rows=1, columns=2):
	
	for i, image in enumerate(images):
		plt.subplot(rows, columns, i+1)
		plt.imshow(image, 'gray')
		plt.title(titles[i])
		plt.xticks([]), plt.yticks([])  
	plt.show()


def show_image(img):
	cv2.imshow('image', img) 
	cv2.waitKey(0) 
	cv2.destroyAllWindows()  


def show_digits(digits, colour=255):
	rows = []
	with_border = [cv2.copyMakeBorder(img.copy(), 1, 1, 1, 1, cv2.BORDER_CONSTANT, None, colour) for img in digits]
	for i in range(9):
		row = np.concatenate(with_border[i * 9:((i + 1) * 9)], axis=1)
		rows.append(row)
	img = np.concatenate(rows)
	return img


def convert_when_colour(colour, img):
	if len(colour) == 3:
		if len(img.shape) == 2:
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		elif img.shape[2] == 1:
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
	return img


def display_points(in_img, points, radius=5, colour=(0, 0, 255)):
	img = in_img.copy()

	if len(colour) == 3:
		if len(img.shape) == 2:
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
		elif img.shape[2] == 1:
			img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

	for point in points:
		img = cv2.circle(img, tuple(int(x) for x in point), radius, colour, -1)
	show_image(img)
	return img


def display_rects(in_img, rects, colour=(0, 0, 255)):

	img = convert_when_colour(colour, in_img.copy())
	for rect in rects:
		img = cv2.rectangle(img, tuple(int(x) for x in rect[0]), tuple(int(x) for x in rect[1]), colour)
	show_image(img)
	return img


def display_contours(in_img, contours, colour=(0, 0, 255), thickness=2):
	img = convert_when_colour(colour, in_img.copy())
	img = cv2.drawContours(img, contours, -1, colour, thickness)
	show_image(img)


def pre_process_image(img, skip_dilate=False):

	proc = cv2.GaussianBlur(img.copy(), (9, 9), 0)

	proc = cv2.adaptiveThreshold(proc, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

	proc = cv2.bitwise_not(proc, proc)

	if not skip_dilate:
		kernel = np.array([[0., 1., 0.], [1., 1., 1.], [0., 1., 0.]], np.uint8)
		proc = cv2.dilate(proc, kernel)

	return proc


def find_corners_of_largest_polygon(img):

	contours, h = cv2.findContours(img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  
	contours = sorted(contours, key=cv2.contourArea, reverse=True)
	polygon = contours[0]  # Largest image

	bottom_right, _ = max(enumerate([pt[0][0] + pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
	top_left, _ = min(enumerate([pt[0][0] + pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
	bottom_left, _ = min(enumerate([pt[0][0] - pt[0][1] for pt in polygon]), key=operator.itemgetter(1))
	top_right, _ = max(enumerate([pt[0][0] - pt[0][1] for pt in polygon]), key=operator.itemgetter(1))

	return [polygon[top_left][0], polygon[top_right][0], polygon[bottom_right][0], polygon[bottom_left][0]]


def distance_between(p1, p2):
	a = p2[0] - p1[0]
	b = p2[1] - p1[1]
	return np.sqrt((a ** 2) + (b ** 2))


def crop_and_warp(img, crop_rect):
	top_left, top_right, bottom_right, bottom_left = crop_rect[0], crop_rect[1], crop_rect[2], crop_rect[3]

	src = np.array([top_left, top_right, bottom_right, bottom_left], dtype='float32')

	side = max([
		distance_between(bottom_right, top_right),
		distance_between(top_left, bottom_left),
		distance_between(bottom_right, bottom_left),
		distance_between(top_left, top_right)
	])

	dst = np.array([[0, 0], [side - 1, 0], [side - 1, side - 1], [0, side - 1]], dtype='float32')

	m = cv2.getPerspectiveTransform(src, dst)

	return cv2.warpPerspective(img, m, (int(side), int(side)))


def infer_grid(img):
	squares = []
	side = img.shape[:1]
	side = side[0] / 9

	for j in range(9):
		for i in range(9):
			p1 = (i * side, j * side) 
			p2 = ((i + 1) * side, (j + 1) * side)  
			squares.append((p1, p2))
	return squares


def cut_from_rect(img, rect):
	return img[int(rect[0][1]):int(rect[1][1]), int(rect[0][0]):int(rect[1][0])]


def scale_and_centre(img, size, margin=0, background=0):
	h, w = img.shape[:2]

	def centre_pad(length):
	
		if length % 2 == 0:
			side1 = int((size - length) / 2)
			side2 = side1
		else:
			side1 = int((size - length) / 2)
			side2 = side1 + 1
		return side1, side2

	def scale(r, x):
		return int(r * x)

	if h > w:
		t_pad = int(margin / 2)
		b_pad = t_pad
		ratio = (size - margin) / h
		w, h = scale(ratio, w), scale(ratio, h)
		l_pad, r_pad = centre_pad(w)
	else:
		l_pad = int(margin / 2)
		r_pad = l_pad
		ratio = (size - margin) / w
		w, h = scale(ratio, w), scale(ratio, h)
		t_pad, b_pad = centre_pad(h)

	img = cv2.resize(img, (w, h))
	img = cv2.copyMakeBorder(img, t_pad, b_pad, l_pad, r_pad, cv2.BORDER_CONSTANT, None, background)
	return cv2.resize(img, (size, size))


def find_largest_feature(inp_img, scan_tl=None, scan_br=None):

	img = inp_img.copy() 
	height, width = img.shape[:2]

	max_area = 0
	seed_point = (None, None)

	if scan_tl is None:
		scan_tl = [0, 0]

	if scan_br is None:
		scan_br = [width, height]

	for x in range(scan_tl[0], scan_br[0]):
		for y in range(scan_tl[1], scan_br[1]):
			if img.item(y, x) == 255 and x < width and y < height:  
				area = cv2.floodFill(img, None, (x, y), 64)
				if area[0] > max_area: 
					max_area = area[0]
					seed_point = (x, y)

	for x in range(width):
		for y in range(height):
			if img.item(y, x) == 255 and x < width and y < height:
				cv2.floodFill(img, None, (x, y), 64)

	mask = np.zeros((height + 2, width + 2), np.uint8) 

	if all([p is not None for p in seed_point]):
		cv2.floodFill(img, mask, seed_point, 255)

	top, bottom, left, right = height, 0, width, 0

	for x in range(width):
		for y in range(height):
			if img.item(y, x) == 64:  
				cv2.floodFill(img, mask, (x, y), 0)

	
			if img.item(y, x) == 255:
				top = y if y < top else top
				bottom = y if y > bottom else bottom
				left = x if x < left else left
				right = x if x > right else right

	bbox = [[left, top], [right, bottom]]
	return img, np.array(bbox, dtype='float32'), seed_point


def extract_digit(img, rect, size):

	digit = cut_from_rect(img, rect)  

	h, w = digit.shape[:2]
	margin = int(np.mean([h, w]) / 2.5)
	_, bbox, seed = find_largest_feature(digit, [margin, margin], [w - margin, h - margin])
	digit = cut_from_rect(digit, bbox)

	w = bbox[1][0] - bbox[0][0]
	h = bbox[1][1] - bbox[0][1]

	if w > 0 and h > 0 and (w * h) > 100 and len(digit) > 0:
		return scale_and_centre(digit, size, 4)
	else:
		return np.zeros((size, size), np.uint8)


def get_digits(img, squares, size):
	digits = []
	img = pre_process_image(img.copy(), skip_dilate=True)
	for square in squares:
		digits.append(extract_digit(img, square, size))
	return digits



def predict_board(path):
	original = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
	processed = pre_process_image(original)
	corners = find_corners_of_largest_polygon(processed)
	cropped = crop_and_warp(original, corners)
	squares = infer_grid(cropped)
	digits = get_digits(cropped, squares, 28)
	warped = show_digits(digits)

	winX = int(warped.shape[1] / 9.0)
	winY = int(warped.shape[0] / 9.0)

	model = load_model("mnistModel.h5")

	# empty lists to capture recognized digits and center co-ordinates of the cells
	numbers = []

	predictions = []
	for y in range(0, warped.shape[0], winY):
		for x in range(0, warped.shape[1], winX):
			window = warped[y : y+winY, x : x+winX]

			if window.shape[0] != winY or window.shape[1] != winX:
				continue

			clone = warped.copy()
			digit = cv2.resize(window, (28,28))
			digit = clear_border(digit)
			pixel = cv2.countNonZero(digit)
			_, digit = cv2.threshold(digit, 0, 255, cv2.THRESH_BINARY_INV)

			if pixel < 20:
		
				number = 0

			else:
				_,digit = cv2.threshold(digit, 0, 255, cv2.THRESH_BINARY_INV)
				digit = digit/255.0
				array = model.predict(digit.reshape(1, 28, 28, 1))
				number = np.argmax(array)

			numbers.append(number)

			cv2.rectangle(clone, (x, y), (x + winX, y + winY), (0, 255, 0), 2)
	
	grid =np.array(numbers).reshape(9,9)

	return grid

print(predict_board('sudoku_original.jpeg'))