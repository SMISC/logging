<?php

/*
|--------------------------------------------------------------------------
| Application Routes
|--------------------------------------------------------------------------
|
| Here is where you can register all of the routes for an application.
| It's a breeze. Simply tell Laravel the URIs it should respond to
| and give it the Closure to execute when that URI is requested.
|
*/

Route::get('/', array('before' => 'auth', 'HomeController@showOverview'));
Route::get('/overview', array('before' => 'auth', 'HomeController@showOverview'));

Route::get('/login', 'LoginController@showLogin');
Route::post('/login', 'LoginController@attemptLogin');
