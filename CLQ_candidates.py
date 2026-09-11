from astropy.io import fits
import numpy as np
import pandas as pd

fits_file = "QSO_cat_iron_cumulative_v0.fits"

with fits.open(fits_file) as hdul:
    data = np.ascontiguousarray(hdul[1].data)

df = pd.DataFrame(data)
print("Initial Data")
print(f"Rows: {len(df)}")
print(f"Unique TARGETIDs: {df['TARGETID'].nunique()}\n")

# Keep ONLY ZWARN == 0 & COADD_FIBERSTATUS == 0
df = df[(df['ZWARN'] == 0) & (df['COADD_FIBERSTATUS'] == 0)]
print("After Quality Filtering (ZWARN=0, FIBERSTATUS=0)")
print(f"Rows: {len(df)}")
print(f"Unique TARGETIDs: {df['TARGETID'].nunique()}\n")

# Redshift Filtering (keep only individual observations where 2.1 <= Z <= 3.5)
df = df[(df['Z'] >= 2.1) & (df['Z'] <= 3.5)]
print("After Redshift Filtering (2.1 <= Z <= 3.5)")
print(f"Rows: {len(df)}")
print(f"Unique TARGETIDs: {df['TARGETID'].nunique()}\n")

# Datetime Conversion & Calculate Duration/Observation Count
df['LASTNIGHT'] = pd.to_datetime(df['LASTNIGHT'].astype(str), format='%Y%m%d')

# Group by TARGETID to find the min, max, and count of remaining observations
duration_df = df.groupby('TARGETID')['LASTNIGHT'].agg(['min', 'max', 'count'])
duration_df['duration_days'] = (duration_df['max'] - duration_df['min']).dt.days

# Keep targets with MORE than 1 observation AND a duration of AT LEAST 7 days
valid_targets = duration_df[(duration_df['count'] > 1) & (duration_df['duration_days'] >= 7)]

df = df[df['TARGETID'].isin(valid_targets.index)]

df = df.merge(valid_targets[['duration_days']], on='TARGETID')

print("After >1 Observation & >= 7 Days Duration Filtering")
print(f"Rows: {len(df)}")
print(f"Unique TARGETIDs: {df['TARGETID'].nunique()}\n")

df = df.sort_values(['duration_days', 'TARGETID'], ascending=[False, True])

output_csv = "CLQ_candidates.csv"
df.to_csv(output_csv, index=False)

print("Final Summary")
print(f"Saved final candidates to: {output_csv}")
print(f"Final remaining rows: {len(df)}")
print(f"Final unique TARGETIDs: {df['TARGETID'].nunique()}")