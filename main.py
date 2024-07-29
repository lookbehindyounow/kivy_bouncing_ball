from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.graphics import Ellipse, Color
from kivy.metrics import dp
from kivy.clock import Clock
from random import random
from math import pi, sin, cos

radius=50
gravity=-2
damping=False
class MainWidget(Widget):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.gravity=gravity
        self.x,self.y=750,300 # initial pos
        self.vx,self.vy=20,10 # initial v
        with self.canvas:
            self.colour=Color(random(),random(),random())
            self.ball=Ellipse(size=(dp(radius),dp(radius)),pos=(self.x,self.y)) # draw ball
        self.button=Button(text="click")
        self.button.bind(on_press=self.ping) # button fires ball in random direction at random |v| from 40-70
        self.add_widget(self.button)
        Clock.schedule_interval(self.update,1/60) # set fps
    
    def update(self,dt): # every frame
        if damping: # drag
            self.vx*=0.995
            self.vy*=0.995
        self.bounced_y=False # if this becomes positive it tells code to skip normal y & vy calculations
        self.x+=self.vx # move x
        boundary=self.width-2*radius # right wall
        if self.x<0:
            self.bounce(False,0) # bounce horizontally against left wall
        elif self.x>boundary:
            self.bounce(False,boundary) # bounce horizontally against right wall
        self.y+=self.vy+self.gravity/2 # move y; s=ut+(at²)/2, t=1
        boundary=self.height-2*radius # top wall
        if self.y<0:
            self.bounce(True,0) # bounce vertically against bottom wall
        elif self.y>boundary:
            self.bounce(True,boundary) # bounce vertically against top wall
        if not self.bounced_y: # normal y & vy calculations
            self.vy+=self.gravity # v=u+at => dv=at, t=1
            # if sign(self.vy)!=sign(self.vy-self.gravity): # if v changed direction without bouncing
            #     s=(self.vy**2)/(2*self.gravity) # s=(v²-u²)/2a, u=0 for s from peak
            #     print(self.y-s) # print peak height
            # print(f"u={self.vy-self.gravity}, a={self.gravity}, post-pos={self.y}, s={self.vy-self.gravity/2}, v={self.vy}, t=1")
            # print()
        self.ball.pos=(self.x,self.y) # update ball pos
    
    def bounce(self,vert,boundary): # every bounce
        if vert: # bounce vertically
            self.bounced_y=True # skip normal y & vy calculations later in this frame
            self.y-=self.vy+self.gravity/2 # undo the move y operation that put us through the wall

            # can't take off constant gravity on bounce frame as acceleration won't remain constant since v changes sign
            # will have to calc effects of acceleration for each side of bounce, splitting frame y movement into two sections
            # for portion of acceleration applied to each half we need portion of frame time before bounce
            # need t, have u, a & s
            # s=ut+(at²)/2
            # (a/2)t²+ut-s=0
            # x=(-b±√(b²-4ac))/2a
            # t=(-u±√( u²-4(a/2)(-s) )) / 2a/2
            # t=(-u±√( u²+2as )) / a
            # we can choose ± by the sign of u because
            # v²=u²+2as
            # & in this case velocity at time of bounce will always be in the same direction as initial velocity
            # (apart from very short bounces where the peak y is reached in the same frame as the bounce which we will handle later)
            # v=sign(u)*√(u²+2as)
            v_bounce=sign(self.vy)*(self.vy**2+2*self.gravity*(boundary-self.y))**0.5
            time_passed=(v_bounce-self.vy)/self.gravity # t=(v-u)/a
            # print(f"u={self.vy}, a={self.gravity}, pre-pos={self.y}, s={boundary+self.vy-self.y}, v={v_bounce}, t={time_passed}")
            t=1-time_passed # post bounce portion of frame time
            self.vy=-v_bounce+self.gravity*t # v=u+at, u=-v_bounce cause post-bounce u is pre-bounce -v
            try: # calculate final post-bounce height
                self.y=boundary+(self.vy**2-v_bounce**2)/(2*self.gravity) # s=(v²-u²)/2a
            except ValueError: # very small bounces throw this error, can consider this to be flat on the ground
                self.gravity=0 # stop pulling down to avoid excess calculation/errors
                self.vy=0
                self.y=0
            # print(f"u={-v_bounce}, a={self.gravity}, post-pos={self.y}, s={self.y-boundary}, v={self.vy}, t={t}")
            # print()
            if damping:
                self.vy*=0.9 # bounce damping
        else: # bounce horizontally
            self.x=2*boundary-self.x # move x was done at start of update, reflect remaining s in bounce wall
            self.vx*=-1 # change x direction
            if damping:
                self.vx*=0.9 # bounce damping
        with self.canvas:
            self.colour.rgba=(random(),random(),random(),1) # change colour
    
    def ping(self,caller): # fire ball
        v=30*random()+40 # at random |v| from 40-70
        θ=random()*2*pi # in random direction
        self.vx=v*sin(θ) # calculate v components
        self.vy=v*cos(θ)
        self.gravity=gravity # reset gravity incase it was 0'd by small bounces

def sign(number): # return sign of number
        return (number>0)-(number<0)

class LabApp(App):
    def build(self):
        return MainWidget() # app is just MainWidget

LabApp().run()