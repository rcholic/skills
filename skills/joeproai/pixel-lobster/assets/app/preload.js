const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('lobsterAPI', {
  getConfig: () => {
    const params = new URLSearchParams(window.location.search);
    return Object.fromEntries(params);
  }
});
