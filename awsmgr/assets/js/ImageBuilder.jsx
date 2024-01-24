"use client";
import React, {useState, useEffect} from 'react';
import axios from 'axios';

function getAxiosInstance() {
  const protocol = window.location.protocol;
  const host = window.location.host;
  const csrfToken = window.csrfToken;
  return axios.create({
    baseURL: `${protocol}//${host}`,
    timeout: 1000,
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    }
  });
}



export default function ImageBuilder(props) {
    console.log("ImageBuilderMaster rendering...")
    // console.log(props);
    // const protocol = window.location.protocol;
    // const host = window.location.host;
    // const csrfToken = window.csrfToken;
    const triggerURL = '/eventstream/v1/aws-ib-trigger-status';
  
    // const instance = axios.create({
    //   baseURL: `${protocol}//${host}`,
    //   timeout: 1000,
    //   headers: {
    //     'Content-Type': 'application/json',
    //     'X-CSRFToken': csrfToken
    //   }
    // });
  
    const axiosInstance = getAxiosInstance();
  
    const [respToken, setRespToken] = useState(); //new EventSource()
    const [imagesData, setImagesData] = useState();
    const [loading, setLoading] = useState(false);
    const [columns, setColumns] = useState([]);
  
    const [count, setCount] = useState(0);
    
    const getData = async () => {
      // This will trigger an event on host to fetch data from AWS
      console.log(`Fetching: ${window.location.protocol}//${window.location.host}/${triggerURL}`)
      try {
        const response = await axiosInstance.get(triggerURL)
        .then((resp) => {
          // let data = resp.data.data
          console.log("***************")
          console.log(resp)
          console.log("***************")
          if(Object.keys(resp.data).includes('token')){
            console.log(`Trigger token ticket returned: ${resp.data.token}`);
            setRespToken(resp.data.token);
          }
        });
      } catch (error) {
        console.error('There was an error!', error);
      }
    };
  
    const handleClick = () => {
      setCount(count+1);
    };
  
    useEffect(() => {
      console.log('This runs once after the initial render');
      setLoading(true);
      getData();
     }, []);
  
    //this.handleClick = this.handleClick.bind(this);
    return (
      <div>
        <button onClick={handleClick}>+1</button>
        <p>{count} : '{loading}'</p>
        <IBTableSSE token={respToken} />
      </div>
    )
  };
  
  // ImageBuilderTable.prototype.render = () => {
  //   return (
  //     <>
  //       <button onClick={setCount(count+1)}>+1</button>
  //       <p>{count}</p>
  //     </>
  //   )
  // };
  
  // ImageBuilderTable.prototype.handleClick = () => {
  //   const { count } = this.state;
  //   this.setState({ count: count + 1 });
  // };
  
  // Object.setPrototypeOf(ImageBuilderTable.prototype, React.Component.prototype);
  
  // export default ImageBuilderTable;