import pandas as pd
import heapq


# reads data from the csv file and specifies what data type each column should be treated as
data = pd.read_csv('AirBNB3.csv', dtype={'price': 'float', 'service fee': 'float',
                                        'review rate number': 'float', 'lat': 'float', 'long': 'float',
                                        'NAME': 'str'})




def sort(array):
   if len(array) <= 1:
       return array


   mid = len(array) // 2
   left = sort(array[:mid])  # recursive call to split the first half of each list
   right = sort(array[mid:])  # recursive call to split the second half of each list
   return merge(left, right)




def merge(left, right):
   ordered = []
   i = j = 0
   while i < len(left) and j < len(right):  # compares the two lists and adds them to one list in order
       if left[i] < right[j]:
           ordered.append(left[i])
           i += 1
       else:
           ordered.append(right[j])
           j += 1


   # adds the leftover elements once one of the lists is empty
   ordered.extend(left[i:])
   ordered.extend(right[j:])
   return ordered




def findTopListings(maxPrice, maxServiceFee, minRating, userLocation=None, maxDistance=None):
   """
   maxPrice: user-entered max price, maxServiceFee: user-entered max service fee,
   minRating: user-entered minimum rating, userLocation: user-entered location in NYC,
   maxDistance: user-entered maximum distance
   """
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
       # pushes the listings into the heap
       rows = filteredListings[filteredListings['price'] == price]
       for _, row in rows.iterrows():
           # heapq in Python is a min-heap by default; -row converts it into a max-heap
           heapq.heappush(max_heap, (-row['price'], -row['review rate number'], row.name))


   # new list for only the 5 returned entries
   topListings = []
   seenListings = set()  # using a set so no duplicates are printed for the result
   while len(topListings) < 5 and max_heap:
       _, _, index = heapq.heappop(max_heap)  # finds the highest priced row and rating and removes it from the heap
       if index not in seenListings:  # if the entry hasn't already been removed
           topListings.append(filteredListings.loc[index])  # gets listing information (name, price, location, etc.)
           seenListings.add(index)  # adds the listing to the set of all listings that have been "visited"


   # converts the list to a dictionary (easier to access & print listing information)
   return [listing.to_dict() for listing in topListings]




maxPrice = 250
maxServiceFee = 50
minRating = 4.5
userLocation = (40.7128, -74.0060)  # Example: NYC coordinates
maxDistance = 0.1  # Example: Approx. 10 km


userListings = findTopListings(maxPrice, maxServiceFee, minRating, userLocation, maxDistance)


# prints the resulting top 5 listings from the csv file based on the user's inputs
for i, listing in enumerate(userListings, 1):
   print(f"Listing {i}:")
   print(f"Name: {listing['NAME']}")
   print(f"Price: ${listing['price']}")
   print(f"Service Fee: ${listing['service fee']}")
   print(f"Rating: {listing['review rate number']}")
   print(f"Location: ({listing['lat']}, {listing['long']})\n")


