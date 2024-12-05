from flask import Flask, request, render_template, jsonify
import pandas as pd
import heapq

app = Flask(__name__)

# reads data from the csv file and specifies what data type each column should be treated as
data = pd.read_csv('AirBNB3.csv', dtype={'price': 'float', 'service fee': 'float',
                                         'review rate number': 'float', 'lat': 'float', 'long': 'float',
                                         'NAME': 'str'})


def sort(array):
    if len(array) <= 1:
        return array
    mid = len(array) // 2
    left = sort(array[:mid])  # recursive call to split the first half of each list
    right = sort(array[mid:]) # second half
    return merge(left, right)


def merge(left, right):
    ordered = []
    i = j = 0
    while i < len(left) and j < len(right): # compares the two lists and adds them to one list in order
        if left[i] < right[j]:
            ordered.append(left[i])
            i += 1
        else:
            ordered.append(right[j])
            j += 1
    ordered.extend(left[i:]) # adds the leftover elements once one of the lists is empty
    ordered.extend(right[j:])
    return ordered


def findTopListings(maxPrice, maxServiceFee, minRating, userLocation=None, maxDistance=None):
    # filters all listings based on the user's desired constraints
    filteredListings = data[(data['price'] <= maxPrice) & (data['service fee'] <= maxServiceFee) &
                            (data['review rate number'] >= minRating)]
    # if a certain location is specified, only return listings within a certain distance from the coordinates
    if userLocation and maxDistance:
        userLatitude, userLongitude = userLocation
        filteredListings = filteredListings[(filteredListings['lat'] - userLatitude) ** 2 +
                                           (filteredListings['long'] - userLongitude) ** 2 <= maxDistance ** 2]

    # calls merge sort on the list of all the prices from the csv file
    prices = sort(filteredListings['price'].tolist())

    # uses a max heap to find the top 5 listings after prices have been sorted
    # max heap was used instead of min heap so all listings wouldn't be the cheapest possible (allowed for variation)

    max_heap = []
    for price in prices:
        rows = filteredListings[filteredListings['price'] == price]
        for _, row in rows.iterrows():
            heapq.heappush(max_heap, (-row['price'], -row['review rate number'], row.name))

    # new list for only the 5 returned entries
    topListings = []
    # using a set so no duplicates are printed for the result
    seenListings = set()
    while len(topListings) < 5 and max_heap:
        _, _, index = heapq.heappop(max_heap)
        # finds the highest priced row and rating and removes it from the heap
        if index not in seenListings:
            topListings.append(filteredListings.loc[index]) # gets necessary info
            seenListings.add(index) # puts dat thing in a list

    return [listing.to_dict() for listing in topListings]
    # converts the list to a dictionary (easier to access & print listing information)

@app.route('/')
def index():
    return render_template('main.html')


@app.route('/results', methods=['POST'])
def results():
    max_rate = request.form.get('max-rate').replace('$', '')
    service_fee = request.form.get('servicefee-max').replace('$', '')
    location = request.form.get('location')
    rating = request.form.get('rating')

    # makes sure user enters viable parameters
    try:
        max_rate = float(max_rate)
        service_fee = float(service_fee)
        rating = float(rating)
        user_location = tuple(map(float, location.split(','))) if location else None
    except ValueError:
        return "Invalid input data. Please check your form.", 400

    # use our previous function to find the best stuff
    top_listings = findTopListings(max_rate, service_fee, rating, user_location)

    # sends it back to continue.html so that it can display the info
    return render_template(
        'continue.html',
        max_rate=max_rate,
        service_fee=service_fee,
        location=location or "Not provided",
        rating=rating,
        top_listings=top_listings
    )




if __name__ == '__main__':
    app.run(debug=True)
