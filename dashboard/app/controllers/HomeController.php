<?php

class HomeController extends BaseController
{
    public function showOverview()
    {
        $this->layout->content = View::make('overview');
    }
}
