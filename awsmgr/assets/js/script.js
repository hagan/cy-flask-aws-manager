// App initialization code goes here
import _version from './version';
import React, { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import AppStream from './AppStream';

if(window.location.pathname === '/') {
    console.log(`${_version} Loading root modules...`);
    // const ipm = new imagePageModule();
    // ipm.init(window.csrfToken);
    
    // 20231108 - disabled React thing
    const container = document.getElementById('root');
    const root = createRoot(container);
    root.render(
      <StrictMode>
        <AppStream />
      </StrictMode>
    );

    function startInstanceClick() {
      console.log("Starting instance...");
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "https://api.data7.net/appstream/demo", true);
      xhr.setRequestHeader("Content-type", "application/json");
      xhr.setRequestHeader("Authorization", `Bearer ${window.bearerToken}`);
      var data = JSON.stringify({'action': 'start'});
      // Define what happens on successful data submission
      xhr.onreadystatechange = function () {
        // Check if the request was successful
        if(xhr.readyState === XMLHttpRequest.DONE) {
          if (xhr.status === 200) {
            console.log(xhr.responseText);
          } else {
            console.error("ERROR occurred: Status code = " + xhr.status);
          }
        }
      };
      xhr.send(data);
    }
    const appStreamButton = document.getElementById('appstreamStartButton');
    appStreamButton.onclick = startInstanceClick;

    function myButtonClick() {
      console.log("Called button click action!");
      var xhr = new XMLHttpRequest();
      xhr.open("GET", window.AWSAppStreamLambdaAPI, true);
      xhr.setRequestHeader("Content-type", "application/json");
      xhr.setRequestHeader("Authorization", `Bearer ${window.bearerToken}`);
      // Define what happens on successful data submission
      xhr.onload = function () {
        // Check if the request was successful
        if (xhr.status >= 200 && xhr.status < 300) {
            // This is where you can handle a successful response
            console.log('Success!', JSON.parse(xhr.responseText));
        } else {
            // This is where you can handle errors
            console.error('The request failed!');
        }
      };
      // Define what happens in case of error
      xhr.onerror = function () {
        console.error('The request failed due to an error!');
      };
      xhr.send();
    }
    const button = document.getElementById('myButton');
    button.onclick = myButtonClick;
    
    // ReactDOM.render(<App ipm={ipm}/>, document.getElementById('root'));
}