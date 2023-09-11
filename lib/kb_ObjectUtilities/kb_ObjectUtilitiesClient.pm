package kb_ObjectUtilities::kb_ObjectUtilitiesClient;

use JSON::RPC::Client;
use POSIX;
use strict;
use Data::Dumper;
use URI;
use Bio::KBase::Exceptions;
my $get_time = sub { time, 0 };
eval {
    require Time::HiRes;
    $get_time = sub { Time::HiRes::gettimeofday() };
};

use Bio::KBase::AuthToken;

# Client version should match Impl version
# This is a Semantic Version number,
# http://semver.org
our $VERSION = "0.1.0";

=head1 NAME

kb_ObjectUtilities::kb_ObjectUtilitiesClient

=head1 DESCRIPTION


** A KBase module: kb_ObjectUtilities
**
** This module contains basic utility Apps for manipulating objects (other than Reads and Sets, which are found in kb_ReadsUtilities and kb_SetUtilities)


=cut

sub new
{
    my($class, $url, @args) = @_;
    

    my $self = {
	client => kb_ObjectUtilities::kb_ObjectUtilitiesClient::RpcClient->new,
	url => $url,
	headers => [],
    };

    chomp($self->{hostname} = `hostname`);
    $self->{hostname} ||= 'unknown-host';

    #
    # Set up for propagating KBRPC_TAG and KBRPC_METADATA environment variables through
    # to invoked services. If these values are not set, we create a new tag
    # and a metadata field with basic information about the invoking script.
    #
    if ($ENV{KBRPC_TAG})
    {
	$self->{kbrpc_tag} = $ENV{KBRPC_TAG};
    }
    else
    {
	my ($t, $us) = &$get_time();
	$us = sprintf("%06d", $us);
	my $ts = strftime("%Y-%m-%dT%H:%M:%S.${us}Z", gmtime $t);
	$self->{kbrpc_tag} = "C:$0:$self->{hostname}:$$:$ts";
    }
    push(@{$self->{headers}}, 'Kbrpc-Tag', $self->{kbrpc_tag});

    if ($ENV{KBRPC_METADATA})
    {
	$self->{kbrpc_metadata} = $ENV{KBRPC_METADATA};
	push(@{$self->{headers}}, 'Kbrpc-Metadata', $self->{kbrpc_metadata});
    }

    if ($ENV{KBRPC_ERROR_DEST})
    {
	$self->{kbrpc_error_dest} = $ENV{KBRPC_ERROR_DEST};
	push(@{$self->{headers}}, 'Kbrpc-Errordest', $self->{kbrpc_error_dest});
    }

    #
    # This module requires authentication.
    #
    # We create an auth token, passing through the arguments that we were (hopefully) given.

    {
	my %arg_hash2 = @args;
	if (exists $arg_hash2{"token"}) {
	    $self->{token} = $arg_hash2{"token"};
	} elsif (exists $arg_hash2{"user_id"}) {
	    my $token = Bio::KBase::AuthToken->new(@args);
	    if (!$token->error_message) {
	        $self->{token} = $token->token;
	    }
	}
	
	if (exists $self->{token})
	{
	    $self->{client}->{token} = $self->{token};
	}
    }

    my $ua = $self->{client}->ua;	 
    my $timeout = $ENV{CDMI_TIMEOUT} || (30 * 60);	 
    $ua->timeout($timeout);
    bless $self, $class;
    #    $self->_validate_version();
    return $self;
}




=head2 KButil_copy_object

  $return = $obj->KButil_copy_object($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_copy_object_Params
$return is a kb_ObjectUtilities.KButil_copy_object_Output
KButil_copy_object_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	input_ref has a value which is a kb_ObjectUtilities.data_obj_ref
	output_name has a value which is a string
workspace_name is a string
data_obj_ref is a string
KButil_copy_object_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_copy_object_Params
$return is a kb_ObjectUtilities.KButil_copy_object_Output
KButil_copy_object_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	input_ref has a value which is a kb_ObjectUtilities.data_obj_ref
	output_name has a value which is a string
workspace_name is a string
data_obj_ref is a string
KButil_copy_object_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string


=end text

=item Description



=back

=cut

 sub KButil_copy_object
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_copy_object (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_copy_object:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_copy_object');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_copy_object",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_copy_object',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_copy_object",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_copy_object',
				       );
    }
}
 


=head2 KButil_Concat_MSAs

  $return = $obj->KButil_Concat_MSAs($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_Concat_MSAs_Params
$return is a kb_ObjectUtilities.KButil_Concat_MSAs_Output
KButil_Concat_MSAs_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	input_refs has a value which is a kb_ObjectUtilities.data_obj_ref
	output_name has a value which is a kb_ObjectUtilities.data_obj_name
	desc has a value which is a string
	blanks_flag has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
data_obj_ref is a string
data_obj_name is a string
bool is an int
KButil_Concat_MSAs_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_Concat_MSAs_Params
$return is a kb_ObjectUtilities.KButil_Concat_MSAs_Output
KButil_Concat_MSAs_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	input_refs has a value which is a kb_ObjectUtilities.data_obj_ref
	output_name has a value which is a kb_ObjectUtilities.data_obj_name
	desc has a value which is a string
	blanks_flag has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
data_obj_ref is a string
data_obj_name is a string
bool is an int
KButil_Concat_MSAs_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref


=end text

=item Description



=back

=cut

 sub KButil_Concat_MSAs
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_Concat_MSAs (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_Concat_MSAs:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_Concat_MSAs');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_Concat_MSAs",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_Concat_MSAs',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_Concat_MSAs",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_Concat_MSAs',
				       );
    }
}
 


=head2 KButil_count_ws_objects

  $return = $obj->KButil_count_ws_objects($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_count_ws_objects_Params
$return is a kb_ObjectUtilities.KButil_count_ws_objects_Output
KButil_count_ws_objects_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	object_types has a value which is a reference to a list where each element is a string
	verbose has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
bool is an int
KButil_count_ws_objects_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
	ws_obj_refs has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string
data_obj_ref is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_count_ws_objects_Params
$return is a kb_ObjectUtilities.KButil_count_ws_objects_Output
KButil_count_ws_objects_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	object_types has a value which is a reference to a list where each element is a string
	verbose has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
bool is an int
KButil_count_ws_objects_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
	ws_obj_refs has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string
data_obj_ref is a string


=end text

=item Description



=back

=cut

 sub KButil_count_ws_objects
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_count_ws_objects (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_count_ws_objects:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_count_ws_objects');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_count_ws_objects",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_count_ws_objects',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_count_ws_objects",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_count_ws_objects',
				       );
    }
}
 


=head2 KButil_hide_ws_objects

  $return = $obj->KButil_hide_ws_objects($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_hide_ws_objects_Params
$return is a kb_ObjectUtilities.KButil_hide_ws_objects_Output
KButil_hide_ws_objects_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	object_types has a value which is a reference to a list where each element is a string
	verbose has a value which is a kb_ObjectUtilities.bool
	hide_all has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
bool is an int
KButil_hide_ws_objects_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string
data_obj_ref is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_hide_ws_objects_Params
$return is a kb_ObjectUtilities.KButil_hide_ws_objects_Output
KButil_hide_ws_objects_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	object_types has a value which is a reference to a list where each element is a string
	verbose has a value which is a kb_ObjectUtilities.bool
	hide_all has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
bool is an int
KButil_hide_ws_objects_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string
data_obj_ref is a string


=end text

=item Description



=back

=cut

 sub KButil_hide_ws_objects
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_hide_ws_objects (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_hide_ws_objects:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_hide_ws_objects');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_hide_ws_objects",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_hide_ws_objects',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_hide_ws_objects",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_hide_ws_objects',
				       );
    }
}
 


=head2 KButil_unhide_ws_objects

  $return = $obj->KButil_unhide_ws_objects($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_unhide_ws_objects_Params
$return is a kb_ObjectUtilities.KButil_unhide_ws_objects_Output
KButil_unhide_ws_objects_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	object_types has a value which is a reference to a list where each element is a string
	verbose has a value which is a kb_ObjectUtilities.bool
	unhide_all has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
bool is an int
KButil_unhide_ws_objects_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string
data_obj_ref is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_unhide_ws_objects_Params
$return is a kb_ObjectUtilities.KButil_unhide_ws_objects_Output
KButil_unhide_ws_objects_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	object_types has a value which is a reference to a list where each element is a string
	verbose has a value which is a kb_ObjectUtilities.bool
	unhide_all has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
bool is an int
KButil_unhide_ws_objects_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string
data_obj_ref is a string


=end text

=item Description



=back

=cut

 sub KButil_unhide_ws_objects
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_unhide_ws_objects (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_unhide_ws_objects:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_unhide_ws_objects');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_unhide_ws_objects",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_unhide_ws_objects',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_unhide_ws_objects",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_unhide_ws_objects',
				       );
    }
}
 


=head2 KButil_update_genome_species_name

  $return = $obj->KButil_update_genome_species_name($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_update_genome_species_name_Params
$return is a kb_ObjectUtilities.KButil_update_genome_species_name_Output
KButil_update_genome_species_name_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	input_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
	species_names has a value which is a string
workspace_name is a string
data_obj_ref is a string
KButil_update_genome_species_name_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_update_genome_species_name_Params
$return is a kb_ObjectUtilities.KButil_update_genome_species_name_Output
KButil_update_genome_species_name_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	input_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
	species_names has a value which is a string
workspace_name is a string
data_obj_ref is a string
KButil_update_genome_species_name_Output is a reference to a hash where the following keys are defined:
	report_name has a value which is a kb_ObjectUtilities.data_obj_name
	report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_name is a string


=end text

=item Description



=back

=cut

 sub KButil_update_genome_species_name
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_update_genome_species_name (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_update_genome_species_name:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_update_genome_species_name');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_update_genome_species_name",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_update_genome_species_name',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_update_genome_species_name",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_update_genome_species_name',
				       );
    }
}
 


=head2 KButil_update_genome_fields_from_files

  $return = $obj->KButil_update_genome_fields_from_files($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_update_genome_fields_from_files_Params
$return is a kb_ObjectUtilities.KButil_update_genome_fields_from_files_Output
KButil_update_genome_fields_from_files_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	target_list_file has a value which is a kb_ObjectUtilities.file_path
	object_newname_file has a value which is a kb_ObjectUtilities.file_path
	species_name_file has a value which is a kb_ObjectUtilities.file_path
	source_file has a value which is a kb_ObjectUtilities.file_path
	domain_file has a value which is a kb_ObjectUtilities.file_path
	genome_type_file has a value which is a kb_ObjectUtilities.file_path
	release_file has a value which is a kb_ObjectUtilities.file_path
	taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
	taxonomy_ncbi_id_file has a value which is a kb_ObjectUtilities.file_path
	genome_qual_scores_file has a value which is a kb_ObjectUtilities.file_path
	gene_functions_file has a value which is a kb_ObjectUtilities.file_path
	keep_spoofed_mRNAs has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
file_path is a string
bool is an int
KButil_update_genome_fields_from_files_Output is a reference to a hash where the following keys are defined:
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_ref is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_update_genome_fields_from_files_Params
$return is a kb_ObjectUtilities.KButil_update_genome_fields_from_files_Output
KButil_update_genome_fields_from_files_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	target_list_file has a value which is a kb_ObjectUtilities.file_path
	object_newname_file has a value which is a kb_ObjectUtilities.file_path
	species_name_file has a value which is a kb_ObjectUtilities.file_path
	source_file has a value which is a kb_ObjectUtilities.file_path
	domain_file has a value which is a kb_ObjectUtilities.file_path
	genome_type_file has a value which is a kb_ObjectUtilities.file_path
	release_file has a value which is a kb_ObjectUtilities.file_path
	taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
	taxonomy_ncbi_id_file has a value which is a kb_ObjectUtilities.file_path
	genome_qual_scores_file has a value which is a kb_ObjectUtilities.file_path
	gene_functions_file has a value which is a kb_ObjectUtilities.file_path
	keep_spoofed_mRNAs has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
file_path is a string
bool is an int
KButil_update_genome_fields_from_files_Output is a reference to a hash where the following keys are defined:
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_ref is a string


=end text

=item Description



=back

=cut

 sub KButil_update_genome_fields_from_files
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_update_genome_fields_from_files (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_update_genome_fields_from_files:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_update_genome_fields_from_files');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_update_genome_fields_from_files",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_update_genome_fields_from_files',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_update_genome_fields_from_files",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_update_genome_fields_from_files',
				       );
    }
}
 


=head2 KButil_update_genome_lineage_from_files

  $return = $obj->KButil_update_genome_lineage_from_files($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_update_genome_lineage_from_files_Params
$return is a kb_ObjectUtilities.KButil_update_genome_lineage_from_files_Output
KButil_update_genome_lineage_from_files_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	target_list_file has a value which is a kb_ObjectUtilities.file_path
	release_file has a value which is a kb_ObjectUtilities.file_path
	taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
	delete_old_taxon_assignments has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
file_path is a string
bool is an int
KButil_update_genome_lineage_from_files_Output is a reference to a hash where the following keys are defined:
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_ref is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_update_genome_lineage_from_files_Params
$return is a kb_ObjectUtilities.KButil_update_genome_lineage_from_files_Output
KButil_update_genome_lineage_from_files_Params is a reference to a hash where the following keys are defined:
	workspace_name has a value which is a kb_ObjectUtilities.workspace_name
	target_list_file has a value which is a kb_ObjectUtilities.file_path
	release_file has a value which is a kb_ObjectUtilities.file_path
	taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
	delete_old_taxon_assignments has a value which is a kb_ObjectUtilities.bool
workspace_name is a string
file_path is a string
bool is an int
KButil_update_genome_lineage_from_files_Output is a reference to a hash where the following keys are defined:
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_ref is a string


=end text

=item Description



=back

=cut

 sub KButil_update_genome_lineage_from_files
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_update_genome_lineage_from_files (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_update_genome_lineage_from_files:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_update_genome_lineage_from_files');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_update_genome_lineage_from_files",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_update_genome_lineage_from_files',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_update_genome_lineage_from_files",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_update_genome_lineage_from_files',
				       );
    }
}
 


=head2 KButil_update_genome_features_from_file

  $return = $obj->KButil_update_genome_features_from_file($params)

=over 4

=item Parameter and return types

=begin html

<pre>
$params is a kb_ObjectUtilities.KButil_update_genome_features_from_file_Params
$return is a kb_ObjectUtilities.KButil_update_genome_features_from_file_Output
KButil_update_genome_features_from_file_Params is a reference to a hash where the following keys are defined:
	feature_update_file has a value which is a kb_ObjectUtilities.file_path
	genome_ref_map has a value which is a kb_ObjectUtilities.file_path
file_path is a string
KButil_update_genome_features_from_file_Output is a reference to a hash where the following keys are defined:
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_ref is a string

</pre>

=end html

=begin text

$params is a kb_ObjectUtilities.KButil_update_genome_features_from_file_Params
$return is a kb_ObjectUtilities.KButil_update_genome_features_from_file_Output
KButil_update_genome_features_from_file_Params is a reference to a hash where the following keys are defined:
	feature_update_file has a value which is a kb_ObjectUtilities.file_path
	genome_ref_map has a value which is a kb_ObjectUtilities.file_path
file_path is a string
KButil_update_genome_features_from_file_Output is a reference to a hash where the following keys are defined:
	updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
data_obj_ref is a string


=end text

=item Description



=back

=cut

 sub KButil_update_genome_features_from_file
{
    my($self, @args) = @_;

# Authentication: required

    if ((my $n = @args) != 1)
    {
	Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
							       "Invalid argument count for function KButil_update_genome_features_from_file (received $n, expecting 1)");
    }
    {
	my($params) = @args;

	my @_bad_arguments;
        (ref($params) eq 'HASH') or push(@_bad_arguments, "Invalid type for argument 1 \"params\" (value was \"$params\")");
        if (@_bad_arguments) {
	    my $msg = "Invalid arguments passed to KButil_update_genome_features_from_file:\n" . join("", map { "\t$_\n" } @_bad_arguments);
	    Bio::KBase::Exceptions::ArgumentValidationError->throw(error => $msg,
								   method_name => 'KButil_update_genome_features_from_file');
	}
    }

    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
	    method => "kb_ObjectUtilities.KButil_update_genome_features_from_file",
	    params => \@args,
    });
    if ($result) {
	if ($result->is_error) {
	    Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
					       code => $result->content->{error}->{code},
					       method_name => 'KButil_update_genome_features_from_file',
					       data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
					      );
	} else {
	    return wantarray ? @{$result->result} : $result->result->[0];
	}
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method KButil_update_genome_features_from_file",
					    status_line => $self->{client}->status_line,
					    method_name => 'KButil_update_genome_features_from_file',
				       );
    }
}
 
  
sub status
{
    my($self, @args) = @_;
    if ((my $n = @args) != 0) {
        Bio::KBase::Exceptions::ArgumentValidationError->throw(error =>
                                   "Invalid argument count for function status (received $n, expecting 0)");
    }
    my $url = $self->{url};
    my $result = $self->{client}->call($url, $self->{headers}, {
        method => "kb_ObjectUtilities.status",
        params => \@args,
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(error => $result->error_message,
                           code => $result->content->{error}->{code},
                           method_name => 'status',
                           data => $result->content->{error}->{error} # JSON::RPC::ReturnObject only supports JSONRPC 1.1 or 1.O
                          );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(error => "Error invoking method status",
                        status_line => $self->{client}->status_line,
                        method_name => 'status',
                       );
    }
}
   

sub version {
    my ($self) = @_;
    my $result = $self->{client}->call($self->{url}, $self->{headers}, {
        method => "kb_ObjectUtilities.version",
        params => [],
    });
    if ($result) {
        if ($result->is_error) {
            Bio::KBase::Exceptions::JSONRPC->throw(
                error => $result->error_message,
                code => $result->content->{code},
                method_name => 'KButil_update_genome_features_from_file',
            );
        } else {
            return wantarray ? @{$result->result} : $result->result->[0];
        }
    } else {
        Bio::KBase::Exceptions::HTTP->throw(
            error => "Error invoking method KButil_update_genome_features_from_file",
            status_line => $self->{client}->status_line,
            method_name => 'KButil_update_genome_features_from_file',
        );
    }
}

sub _validate_version {
    my ($self) = @_;
    my $svr_version = $self->version();
    my $client_version = $VERSION;
    my ($cMajor, $cMinor) = split(/\./, $client_version);
    my ($sMajor, $sMinor) = split(/\./, $svr_version);
    if ($sMajor != $cMajor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Major version numbers differ.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor < $cMinor) {
        Bio::KBase::Exceptions::ClientServerIncompatible->throw(
            error => "Client minor version greater than Server minor version.",
            server_version => $svr_version,
            client_version => $client_version
        );
    }
    if ($sMinor > $cMinor) {
        warn "New client version available for kb_ObjectUtilities::kb_ObjectUtilitiesClient\n";
    }
    if ($sMajor == 0) {
        warn "kb_ObjectUtilities::kb_ObjectUtilitiesClient version is $svr_version. API subject to change.\n";
    }
}

=head1 TYPES



=head2 workspace_name

=over 4



=item Description

** The workspace object refs are of form:
**
**    objects = ws.get_objects([{'ref': params['workspace_id']+'/'+params['obj_name']}])
**
** "ref" means the entire name combining the workspace id and the object name
** "id" is a numerical identifier of the workspace or object, and should just be used for workspace
** "name" is a string identifier of a workspace or object.  This is received from Narrative.


=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 file_path

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 sequence

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 data_obj_name

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 data_obj_ref

=over 4



=item Definition

=begin html

<pre>
a string
</pre>

=end html

=begin text

a string

=end text

=back



=head2 bool

=over 4



=item Definition

=begin html

<pre>
an int
</pre>

=end html

=begin text

an int

=end text

=back



=head2 KButil_copy_object_Params

=over 4



=item Description

KButil_copy_object()
**
**  Method for copying an object of a limited number of common types


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
input_ref has a value which is a kb_ObjectUtilities.data_obj_ref
output_name has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
input_ref has a value which is a kb_ObjectUtilities.data_obj_ref
output_name has a value which is a string


=end text

=back



=head2 KButil_copy_object_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_Concat_MSAs_Params

=over 4



=item Description

KButil_Concat_MSAs()
**
**  Method for Concatenating MSAs into a combined MSA


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
input_refs has a value which is a kb_ObjectUtilities.data_obj_ref
output_name has a value which is a kb_ObjectUtilities.data_obj_name
desc has a value which is a string
blanks_flag has a value which is a kb_ObjectUtilities.bool

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
input_refs has a value which is a kb_ObjectUtilities.data_obj_ref
output_name has a value which is a kb_ObjectUtilities.data_obj_name
desc has a value which is a string
blanks_flag has a value which is a kb_ObjectUtilities.bool


=end text

=back



=head2 KButil_Concat_MSAs_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_count_ws_objects_Params

=over 4



=item Description

KButil_count_ws_objects()
**
**  Method for counting number of workspace objects when data panel fails


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
object_types has a value which is a reference to a list where each element is a string
verbose has a value which is a kb_ObjectUtilities.bool

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
object_types has a value which is a reference to a list where each element is a string
verbose has a value which is a kb_ObjectUtilities.bool


=end text

=back



=head2 KButil_count_ws_objects_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
ws_obj_refs has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
ws_obj_refs has a value which is a reference to a hash where the key is a string and the value is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_hide_ws_objects_Params

=over 4



=item Description

KButil_hide_ws_objects()
**
**  Method for hiding workspace objects in bulk


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
object_types has a value which is a reference to a list where each element is a string
verbose has a value which is a kb_ObjectUtilities.bool
hide_all has a value which is a kb_ObjectUtilities.bool

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
object_types has a value which is a reference to a list where each element is a string
verbose has a value which is a kb_ObjectUtilities.bool
hide_all has a value which is a kb_ObjectUtilities.bool


=end text

=back



=head2 KButil_hide_ws_objects_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_unhide_ws_objects_Params

=over 4



=item Description

KButil_unhide_ws_objects()
**
**  Method for unhiding workspace objects in bulk


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
object_types has a value which is a reference to a list where each element is a string
verbose has a value which is a kb_ObjectUtilities.bool
unhide_all has a value which is a kb_ObjectUtilities.bool

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
object_types has a value which is a reference to a list where each element is a string
verbose has a value which is a kb_ObjectUtilities.bool
unhide_all has a value which is a kb_ObjectUtilities.bool


=end text

=back



=head2 KButil_unhide_ws_objects_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_update_genome_species_name_Params

=over 4



=item Description

KButil_update_genome_species_name()
**
**  Method for adding/changing Genome objects species names


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
input_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
species_names has a value which is a string

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
input_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref
species_names has a value which is a string


=end text

=back



=head2 KButil_update_genome_species_name_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
report_name has a value which is a kb_ObjectUtilities.data_obj_name
report_ref has a value which is a kb_ObjectUtilities.data_obj_ref
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_update_genome_fields_from_files_Params

=over 4



=item Description

KButil_update_genome_fields_from_files()
**
**  Method for adding/changing values in Genome object fields, from files


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
target_list_file has a value which is a kb_ObjectUtilities.file_path
object_newname_file has a value which is a kb_ObjectUtilities.file_path
species_name_file has a value which is a kb_ObjectUtilities.file_path
source_file has a value which is a kb_ObjectUtilities.file_path
domain_file has a value which is a kb_ObjectUtilities.file_path
genome_type_file has a value which is a kb_ObjectUtilities.file_path
release_file has a value which is a kb_ObjectUtilities.file_path
taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
taxonomy_ncbi_id_file has a value which is a kb_ObjectUtilities.file_path
genome_qual_scores_file has a value which is a kb_ObjectUtilities.file_path
gene_functions_file has a value which is a kb_ObjectUtilities.file_path
keep_spoofed_mRNAs has a value which is a kb_ObjectUtilities.bool

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
target_list_file has a value which is a kb_ObjectUtilities.file_path
object_newname_file has a value which is a kb_ObjectUtilities.file_path
species_name_file has a value which is a kb_ObjectUtilities.file_path
source_file has a value which is a kb_ObjectUtilities.file_path
domain_file has a value which is a kb_ObjectUtilities.file_path
genome_type_file has a value which is a kb_ObjectUtilities.file_path
release_file has a value which is a kb_ObjectUtilities.file_path
taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
taxonomy_ncbi_id_file has a value which is a kb_ObjectUtilities.file_path
genome_qual_scores_file has a value which is a kb_ObjectUtilities.file_path
gene_functions_file has a value which is a kb_ObjectUtilities.file_path
keep_spoofed_mRNAs has a value which is a kb_ObjectUtilities.bool


=end text

=back



=head2 KButil_update_genome_fields_from_files_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_update_genome_lineage_from_files_Params

=over 4



=item Description

KButil_update_genome_lineage_from_files()
**
**  Method for adding/changing values in Genome object tax and lineage fields, from files


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
target_list_file has a value which is a kb_ObjectUtilities.file_path
release_file has a value which is a kb_ObjectUtilities.file_path
taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
delete_old_taxon_assignments has a value which is a kb_ObjectUtilities.bool

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
workspace_name has a value which is a kb_ObjectUtilities.workspace_name
target_list_file has a value which is a kb_ObjectUtilities.file_path
release_file has a value which is a kb_ObjectUtilities.file_path
taxonomy_hierarchy_file has a value which is a kb_ObjectUtilities.file_path
delete_old_taxon_assignments has a value which is a kb_ObjectUtilities.bool


=end text

=back



=head2 KButil_update_genome_lineage_from_files_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=head2 KButil_update_genome_features_from_file_Params

=over 4



=item Description

KButil_update_genome_features_from_file()
**
**  Method for adding values to Genome object features, from file


=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
feature_update_file has a value which is a kb_ObjectUtilities.file_path
genome_ref_map has a value which is a kb_ObjectUtilities.file_path

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
feature_update_file has a value which is a kb_ObjectUtilities.file_path
genome_ref_map has a value which is a kb_ObjectUtilities.file_path


=end text

=back



=head2 KButil_update_genome_features_from_file_Output

=over 4



=item Definition

=begin html

<pre>
a reference to a hash where the following keys are defined:
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref

</pre>

=end html

=begin text

a reference to a hash where the following keys are defined:
updated_object_refs has a value which is a reference to a list where each element is a kb_ObjectUtilities.data_obj_ref


=end text

=back



=cut

package kb_ObjectUtilities::kb_ObjectUtilitiesClient::RpcClient;
use base 'JSON::RPC::Client';
use POSIX;
use strict;

#
# Override JSON::RPC::Client::call because it doesn't handle error returns properly.
#

sub call {
    my ($self, $uri, $headers, $obj) = @_;
    my $result;


    {
	if ($uri =~ /\?/) {
	    $result = $self->_get($uri);
	}
	else {
	    Carp::croak "not hashref." unless (ref $obj eq 'HASH');
	    $result = $self->_post($uri, $headers, $obj);
	}

    }

    my $service = $obj->{method} =~ /^system\./ if ( $obj );

    $self->status_line($result->status_line);

    if ($result->is_success) {

        return unless($result->content); # notification?

        if ($service) {
            return JSON::RPC::ServiceObject->new($result, $self->json);
        }

        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    elsif ($result->content_type eq 'application/json')
    {
        return JSON::RPC::ReturnObject->new($result, $self->json);
    }
    else {
        return;
    }
}


sub _post {
    my ($self, $uri, $headers, $obj) = @_;
    my $json = $self->json;

    $obj->{version} ||= $self->{version} || '1.1';

    if ($obj->{version} eq '1.0') {
        delete $obj->{version};
        if (exists $obj->{id}) {
            $self->id($obj->{id}) if ($obj->{id}); # if undef, it is notification.
        }
        else {
            $obj->{id} = $self->id || ($self->id('JSON::RPC::Client'));
        }
    }
    else {
        # $obj->{id} = $self->id if (defined $self->id);
	# Assign a random number to the id if one hasn't been set
	$obj->{id} = (defined $self->id) ? $self->id : substr(rand(),2);
    }

    my $content = $json->encode($obj);

    $self->ua->post(
        $uri,
        Content_Type   => $self->{content_type},
        Content        => $content,
        Accept         => 'application/json',
	@$headers,
	($self->{token} ? (Authorization => $self->{token}) : ()),
    );
}



1;
