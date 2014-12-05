<?php

class HomeController extends BaseController
{
    public function showOverview()
    {
        $redis = LaravelRedis::connection('pacsocial');

        $this->layout->content = View::make('overview')->with(array(
            'info' => $redis->llen('info'),
            'followers' => $redis->llen('followers'),
            'tweets' => $redis->llen('tweets'),
            'logged_in' => true,
            'page' => BaseController::PAGE_SCORES
        ));
    }
}
