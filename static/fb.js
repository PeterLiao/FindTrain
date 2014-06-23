/**
 * Created by peter_c_liao on 6/12/2014.
 */
  // This is called with the results from from FB.getLoginStatus().
  function statusChangeCallback(response) {
    var fb_connected = false;
    //console.log('statusChangeCallback');
    //console.log(response);
    // The response object is returned with a status field that lets the
    // app know the current login status of the person.
    // Full docs on the response object can be found in the documentation
    // for FB.getLoginStatus().
    if (response.status === 'connected') {
      // Logged into your app and Facebook.
      fb_connected = true;
      testAPI();
    } else if (response.status === 'not_authorized') {
      fb_connected = false;
    } else {
      fb_connected = false;
    }
    console.log(response);
    fb_status_change_callback(fb_connected, response);
  }

  // This function is called when someone finishes with the Login
  // Button.  See the onlogin handler attached to it in the sample
  // code below.
  function checkLoginState() {
    FB.getLoginStatus(function(response) {
      statusChangeCallback(response);
    });
  }

  function loginToFB() {
     var fb_logged = false;
      FB.login(function(response) {
        console.log(response)
        if (response.status === 'connected') {
            fb_logged = true;
            testAPI();
        } else if (response.status === 'not_authorized') {
            fb_logged = false;
        } else {
            fb_logged = false;
        }
          console.log(response);
         fb_login_callback(fb_logged, response);
     }, {scope: 'public_profile,email,user_likes'});
  }

  function logoutFB() {
    FB.logout(function(response) {
        fb_logout_callback();
    });
  }

  window.fbAsyncInit = function() {
      FB.init({
        appId      : '1431824143754254', //real- 1431824143754254, test-1431824467087555
        cookie     : true,  // enable cookies to allow the server to access
                            // the session
        xfbml      : true,  // parse social plugins on this page
        version    : 'v2.0' // use version 2.0
      });

      // Now that we've initialized the JavaScript SDK, we call
      // FB.getLoginStatus().  This function gets the state of the
      // person visiting this page and can return one of three states to
      // the callback you provide.  They can be:
      //
      // 1. Logged into your app ('connected')
      // 2. Logged into Facebook, but not your app ('not_authorized')
      // 3. Not logged into Facebook and can't tell if they are logged into
      //    your app or not.
      //
      // These three cases are handled in the callback function.

      FB.getLoginStatus(function(response) {
        statusChangeCallback(response);
      });

  };

  // Load the SDK asynchronously
  (function(d, s, id) {
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) return;
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
  }(document, 'script', 'facebook-jssdk'));

  // Here we run a very simple test of the Graph API after login is
  // successful.  See statusChangeCallback() for when this call is made.
  function testAPI() {
    //console.log('Welcome!  Fetching your information.... ');
    FB.api('/me', function(response) {
      //console.log('Successful login for: ' + response.name);
      console.log(response);
        fb_profile_ready_callback(response);
    });
  }