import bz2
import pickle

# This loads your giant 100MB+ file
print("Loading original file... please wait.")
with open('similarity.pkl', 'rb') as f:
    data = pickle.load(f)

# This saves it into a much smaller 'compressed' format
print("Compressing... this might take a minute.")
with bz2.BZ2File('similarity.pkl.pbz2', 'w') as f:
    pickle.dump(data, f)

print("Done! You now have a new file called: similarity.pkl.pbz2")