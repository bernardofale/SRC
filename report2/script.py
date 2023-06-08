import pandas as pd
import numpy as np
import ipaddress
import dns.resolver
import dns.reversename
import pygeoip
import matplotlib.pyplot as plt 

datafile='dataset8/test8.parquet'

### IP geolocalization
gi=pygeoip.GeoIP('GeoIP_DBs/GeoIP.dat')
gi2=pygeoip.GeoIP('GeoIP_DBs/GeoIPASNum.dat')
addr='193.136.73.21'
cc=gi.country_code_by_addr(addr)
org=gi2.org_by_addr(addr)
#print(cc,org)

### DNS resolution
addr=dns.resolver.resolve("www.ua.pt", 'A')
for a in addr:
    pass
    #print(a)
    
### Reverse DNS resolution    
name=dns.reversename.from_address("193.136.172.20")
addr=dns.resolver.resolve(name, 'PTR')
for a in addr:
    pass
    #print(a)

### Read parquet data files
df=pd.read_parquet(datafile)

# Filter for connections with port 53 and protocol UDP
filtered_df = df[(df['port'] == 53) & (df['proto'] == 'udp')]

# Count the occurrences of each destination IP
connection_counts = filtered_df['dst_ip'].value_counts().reset_index()
connection_counts.columns = ['dst_ip', 'connection_count']

# Sort the result in ascending order based on the destination IP
connection_counts = connection_counts.sort_values('dst_ip', ascending=True)

connection_counts.to_csv('multiple_connections.csv', index=False)

'''
# Get unique source IPs
unique_src_ips = df['src_ip'].unique()

# Get unique destination IPs
unique_dst_ips = df['dst_ip'].unique()

with open('unique_src_ips.txt', 'w+') as f:
    for ip in unique_src_ips:
        f.write(ip + '\n')

with open('unique_dst_ips.txt', 'w+') as f:
    for ip in unique_dst_ips:
        cc=gi.country_code_by_addr(ip)
        org=gi2.org_by_addr(ip)
        if (cc is None or org is None):
            f.write(ip + '\n')
           
        else:
            f.write(ip + ' ' + cc + ' ' + org + '\n')
           ''' 


'''
# Convert the 'timestamp' column to pandas datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s') + pd.to_timedelta(df['timestamp'].astype(int) * 10, unit='ms')


with open('data.csv', 'w+') as f:
    df.to_csv(f)




from scipy import stats

# Select the columns for analysis
selected_columns = ["src_ip", "dst_ip", "up_bytes", "down_bytes"]
df_selected = df[selected_columns]

# Calculate the Z-scores for up_bytes and down_bytes columns
df_selected["up_bytes_zscore"] = stats.zscore(df_selected["up_bytes"])
df_selected["down_bytes_zscore"] = stats.zscore(df_selected["down_bytes"])

# Identify connections with Z-scores above a certain threshold
threshold = 3  # Adjust this value based on your data and requirements
df_selected["is_outlier"] = (df_selected["up_bytes_zscore"].abs() > threshold) | (df_selected["down_bytes_zscore"].abs() > threshold)

with open('anom_outliers_data.csv', 'w+') as f:
    df_selected.to_csv(f)


# Calculate the total data transfer for each connection
df["total_bytes"] = df["up_bytes"] + df["down_bytes"]

# Calculate the mean and standard deviation of the total data transfer
mean_bytes = df["total_bytes"].mean()
std_bytes = df["total_bytes"].std()
print(mean_bytes)
print(std_bytes)

# Set the threshold for identifying unusually large or small values
threshold = 10 # Adjust this value based on your data and requirements

# Identify unusually large or small values
df["is_anomalous"] = (df["total_bytes"] > mean_bytes + threshold * std_bytes) | (df["total_bytes"] < mean_bytes - threshold * std_bytes)

anomalous_df = df[df["is_anomalous"]]
anomalous_df = anomalous_df.sort_values(by="total_bytes", ascending=False)
anomalous_df.to_csv("anomalous_devices.csv", index=False)



# Group the data by source IP
grouped_data = df.groupby("src_ip")

# Calculate the download/upload amounts, ratio, and number of connections
summary_data = grouped_data.agg(
    download_amount=("down_bytes", "sum"),
    upload_amount=("up_bytes", "sum"),
    upload_download_ratio=("up_bytes", lambda x: x.sum() / grouped_data.get_group(x.name)["down_bytes"].sum()),
    connection_count=("src_ip", "count")
)
summary_data = summary_data.sort_values("connection_count", ascending=False)

with open('anom_summary_data.csv', 'w+') as f:
    summary_data.to_csv(f)

    


# Filter TCP and UDP data
tcp_data = df[df["proto"] == "tcp"]
udp_data = df[df["proto"] == "udp"]

# TCP Up Bytes vs. Down Bytes
plt.scatter(tcp_data["up_bytes"], tcp_data["down_bytes"])
plt.xlabel("TCP Up Bytes")
plt.ylabel("TCP Down Bytes")
plt.title("TCP Up Bytes vs. Down Bytes")
plt.show()

# UDP Up Bytes vs. Down Bytes
plt.scatter(udp_data["up_bytes"], udp_data["down_bytes"])
plt.xlabel("UDP Up Bytes")
plt.ylabel("UDP Down Bytes")
plt.title("UDP Up Bytes vs. Down Bytes")
plt.show()

# TCP Up Bytes Distribution
plt.hist(tcp_data["up_bytes"], bins=3)
plt.xlabel("TCP Up Bytes")
plt.ylabel("Frequency")
plt.title("Histogram of TCP Up Bytes")
plt.show()

# UDP Up Bytes Distribution
plt.hist(udp_data["up_bytes"], bins=3)
plt.xlabel("UDP Up Bytes")
plt.ylabel("Frequency")
plt.title("Histogram of UDP Up Bytes")
plt.show()


# Plotting a histogram
plt.hist(df["up_bytes"], bins=3)
plt.xlabel("Up Bytes")
plt.ylabel("Frequency")
plt.title("Histogram of Up Bytes")
plt.show()

# Plotting a line chart
plt.plot(df["timestamp"], df["down_bytes"])
plt.xlabel("Timestamp")
plt.ylabel("Down Bytes")
plt.title("Line Chart of Down Bytes over Time")
plt.show()

# Plotting a scatter plot
plt.scatter(df["up_bytes"], df["down_bytes"])
plt.xlabel("Up Bytes")
plt.ylabel("Down Bytes")
plt.title("Scatter Plot of Up Bytes vs. Down Bytes")
plt.show()

# Bar chart
protocol_counts = df["proto"].value_counts()
plt.bar(protocol_counts.index, protocol_counts.values)
plt.xlabel("Protocol")
plt.ylabel("Count")
plt.title("Protocol Distribution")
plt.xticks(rotation=90)
plt.show()

# Box plot
plt.boxplot([df["up_bytes"], df["down_bytes"]])
plt.xticks([1, 2], ["Up Bytes", "Down Bytes"])
plt.ylabel("Bytes")
plt.title("Box Plot of Up Bytes and Down Bytes")
plt.show()

# Line chart with multiple lines
df_grouped = df.groupby("timestamp").agg({"up_bytes": "sum", "down_bytes": "sum"})
plt.plot(df_grouped.index, df_grouped["up_bytes"], label="Up Bytes")
plt.plot(df_grouped.index, df_grouped["down_bytes"], label="Down Bytes")
plt.xlabel("Timestamp")
plt.ylabel("Bytes")
plt.title("Bytes Transferred over Time")
plt.legend()
plt.show()

#Just the UDP flows
#udpF=data.loc[data['proto']=='udp']

#Number of UDP flows for each source IP
#nudpF=data.loc[data['proto']=='udp'].groupby(['src_ip'])['up_bytes'].count()

#Number of UDP flows to port 443, for each source IP
#nudpF443=data.loc[(data['proto']=='udp')&(data['port']==443)].groupby(['src_ip'])['up_bytes'].count()

#Average number of downloaded bytes, per flow, for each source IP
#avgUp=data.groupby(['src_ip'])['down_bytes'].mean()

### Read parquet data files
data=pd.read_parquet(datafile)

#Total uploaded bytes to destination port 443, for each source IP, ordered from larger amount to lowest amount
#upS=data.loc[((data['port']==443))].groupby(['src_ip'])['up_bytes'].sum().sort_values(ascending=False)

#Histogram of the total uploaded bytes to destination port 443, by source IP
#upS=data.loc[((data['port']==443))].groupby(['src_ip'])['up_bytes'].sum().hist()


#Is destination IPv4 a public address?
NET=ipaddress.IPv4Network('192.168.108.0/24')
bpublic=data.apply(lambda x: ipaddress.IPv4Address(x['dst_ip']) not in NET,axis=1)

#Geolocalization of public destination adddress
cc=data[bpublic]['dst_ip'].apply(lambda y:gi.country_code_by_addr(y)).to_frame(name='cc')
'''