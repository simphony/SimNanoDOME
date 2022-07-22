FROM registry.gitlab.cc-asp.fraunhofer.de:4567/mat-info/nanodome-interactive:latest

SHELL ["/bin/bash", "-c"]

#change user
USER root

#go to home dir and copy files into container
WORKDIR /home/simnanodome
COPY . .

#install osp-core, simopenfoam and related ontology
#(in case of cloning OSP-core from Gitlab)
RUN source $HOME/.bashrc && \
    cd osp-core && \
    python3.7 setup.py develop && \
    cd .. && \
    python3.7 setup.py develop && \
    cd .. && \
    chown -R simphony:simphony /home/simnanodome \
			       /home/simnanodome/osp-core \
			       /home/simnanodome/ontology	
##install simopenfoam 
#(in case of that osp-core is already installed)
#RUN sizrce $HOME/.bashrc && \
#    python3.7 setup.py develop && \
#    chown -R simphony:simphony /home/simopenfoam 

#switch user
USER simphony

#give simphony the user rights
RUN chmod -R a=rwx /home/simnanodome
RUN source $HOME/.bashrc

#install ontology
RUN pico install /home/simnanodome/ontology/ontology.simnanofoam.yml
