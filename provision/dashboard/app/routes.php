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

Route::get('/', array(
    'as' => 'scores-index',
    'before' => 'auth.single', 
    'uses' => 'ScoresController@showTeams'
));

Route::get('scores', array(
    'as' => 'scores-list',
    'before' => 'auth.single', 
    'uses' => 'ScoresController@showTeams'
));

Route::get('team/{team}', array(
    'as' => 'scores-team',
    'before' => 'auth.single', 
    'uses' => 'ScoresController@showTeam'
));

Route::get('diagnostics', array(
    'as' => 'diagnostics',
    'before' => 'auth.single', 
    'uses' => 'DiagnosticsController@showOverview'
));


Route::get('login', array(
    'as' => 'login',
    'uses' => 'LoginController@showLogin'
));

Route::post('login', 'LoginController@attemptLogin');
