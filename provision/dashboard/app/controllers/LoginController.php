<?php

class LoginController extends BaseController
{
    public function showLogin()
    {
        $this->layout->content = View::make('login')->with('message', Session::get('message', ''));
    }

    public function attemptLogin()
    {
        $password = Input::get('password');
        
        if(hash('sha256', $password) === Config::get('app.authentication_secret')) {
            Session::set(Config::get('app.authentication_session_key'), true);

            return Redirect::intended('/overview');
        } else {
            return Redirect::to('login')->with('message', 'Login failed');
        }
    }
}
