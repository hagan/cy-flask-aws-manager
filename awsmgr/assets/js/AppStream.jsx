"use client";
import React, {useState, useEffect, useRef} from 'react';
import axios from 'axios';

function getAxiosInstance(protocol, host, bearerToken) {
//   const protocol = window.location.protocol;
//   const host = window.location.host;
//   const csrfToken = window.csrfToken;

  // CORS error in firefox from localhost fix::
  // about:config => security.fileuri.strict_origin_policy => false
  console.log(`Bearer Token: >${bearerToken}<`);
  return axios.create({
    baseURL: `${protocol}//${host}`,
    timeout: 1000,
    withCredentials: true,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${bearerToken}`,
    //   'X-CSRFToken': csrfToken
    }
  });
}

export default function AppStream(props) {
    console.log(`AppStream rendering => ${window.AWSAppStreamLambdaAPI}`);
    const awsAppStreamURL = new URL(window.AWSAppStreamLambdaAPI);
    const protocol = awsAppStreamURL.protocol;
    const host = awsAppStreamURL.host;
    const pathname = awsAppStreamURL.pathname;
    const bearerToken = window.bearerToken;
    console.log(host);

    const loadingRef = useRef(null);
    const axiosInstance = getAxiosInstance(protocol, host, bearerToken);
    const [isLoading, setIsLoading] = useState(true);
    const [streamingURL, setstreamingURL] = useState('none');

    const getData = async () => {
      // This will trigger an event on host to fetch data from AWS
      console.log(`Fetching: ${protocol}//${host}${pathname}`);

      // , {
      //   headers: {
      //     'Authorization': `Bearer ${bearerToken}`
      //   }
      // }

      try {
        const response = await axiosInstance.get(pathname)
        .then((resp) => {
          let data = resp.data.appstream_streaming_url
          setstreamingURL(data);
          setIsLoading(false);
          // if(Object.keys(resp.data).includes('token')){
          //   console.log(`Trigger token ticket returned: ${resp.data.token}`);
          //   setRespToken(resp.data.token);
          // }
          // const eventToken = resp.data
          // return resp.data.json();
        });
        // .then((data) => {
        //   console.log(data);
  
        //   // LAST STEP!
        //   setLoading(false);
        // });
      } catch (error) {
        console.error('There was an error!');
      }
    };

    useEffect(() => {
        console.log('This runs once after the initial render');
        setIsLoading(true);
        getData();
    }, []); // should only load at startup

    const handleClick = () => {
        setIsLoading(true);
        getData();
    };

    return (
        <div>
          <button onClick={handleClick}>Fetch URL</button>
          {isLoading ? (
              <div ref={loadingRef}>Loading...</div>
            ) : (
              <p><a href={streamingURL} target="_blank">{streamingURL}</a></p>
            )}
        </div>
    )
};
