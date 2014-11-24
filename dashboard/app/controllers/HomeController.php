<?php

class HomeController extends BaseController
{
    public function showOverview()
    {
        $redis = LaravelRedis::connection('pacsocial');

        $this->layout->content = View::make('overview')->with(array(
            'edges' => $redis->llen('followers')
        ));
    }
}
