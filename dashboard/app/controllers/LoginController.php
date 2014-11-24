<?php

class LoginController extends BaseController
{
    public function showLogin()
    {
        $this->layout->content = View::make('login');
    }

    public function attemptLogin()
    {
        $username = Input::get('username');
        $password = Input::get('password');
        
        if(Auth::attempt(array('username' => $username, 'password' => $password))) {
            return Redirect::intended('/overview');
        }
    }
}
