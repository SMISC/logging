<?php

class LoginController extends BaseController
{
    public function showLogin()
    {
        $this->layout->content = View::make('login')->with('message', Session::get('message', ''));
    }

    public function attemptLogin()
    {
        $username = Input::get('username');
        $password = Input::get('password');
        
        if(Auth::attempt(array('username' => $username, 'password' => $password))) {
            return Redirect::intended('/overview');
        } else {
            return Redirect::to('login')->with('message', 'Login failed');
        }
    }
}
