/**
 * Image hash utilities for frontend
 */

/**
 * Calculate SHA-256 hash of a file
 * @param {File} file - The file to hash
 * @returns {Promise<string>} - Promise resolving to hash string
 */
export const calculateFileHash = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = async (event) => {
      const arrayBuffer = event.target.result;
      
      try {
        // Use the Web Crypto API to calculate SHA-256 hash
        const hashBuffer = await crypto.subtle.digest('SHA-256', arrayBuffer);
        
        // Convert the hash to hex string
        const hashArray = Array.from(new Uint8Array(hashBuffer));
        const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
        
        resolve(hashHex);
      } catch (error) {
        reject(error);
      }
    };
    
    reader.onerror = () => {
      reject(new Error('Error reading file'));
    };
    
    reader.readAsArrayBuffer(file);
  });
};

/**
 * Extract file extension with the dot
 * @param {string} filename - The filename
 * @returns {string} - File extension with dot (e.g., ".jpg")
 */
export const getFileExtension = (filename) => {
  return filename.substring(filename.lastIndexOf('.'));
}; 