<?php

class LoginController extends BaseController
{
    public function showLogin()
    {
        $this->layout->content = View::make('login')->with(array(
            'message' => Session::get('message', '')
        ));
    }

    public function attemptLogin()
    {
        $password = Input::get('password');
        
        if(in_array(hash('sha256', $password), Config::get('app.authentication_secrets'))) {
            Session::set(Config::get('app.authentication_session_key'), true);

            return Redirect::intended('/overview');
        } else {
            return Redirect::to('login')->with('message', 'Login failed');
        }
    }
}
