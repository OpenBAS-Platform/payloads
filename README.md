# OpenBAS Payload Repository

## 📜 Scripts

### 🔄 JSON Merger Script

**Standalone Node.js script** (`compute-json.js`) that **recursively scans a directory** for `.json` files and merges
them into a single file.

#### 🔍 How It Works

- **Scans** the given directory and its subdirectories.
- **Finds all `.json` files** and reads their content.
- **Concatenates** all JSON objects into a list.
- **Saves the result** in a single `merged.json` file.

#### 🛠 Usage

##### 📥 Install Node.js (if needed)

Download it from [nodejs.org](https://nodejs.org/).

##### 🚀 Run the script

Execute the script with:

```sh
node scripts/compute-json.js
```  

##### 📂 Output

📄 A new file `merged.json` will be created in the **indexes folder**, containing all JSON objects **merged into an array
**. 🎯  
